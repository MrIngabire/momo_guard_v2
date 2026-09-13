import os
import json
import re
import joblib
import numpy as np

from google import genai
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from app.config import settings
from app.training_data import TRAINING_DATA

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "rf_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "metrics.json")

CONFIDENCE_LOW = 0.15
CONFIDENCE_HIGH = 0.85

_gemini_client = None
if settings.GEMINI_API_KEY:
    _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
else:
    print("[ML] WARNING: GEMINI_API_KEY not set — Gemini fallback disabled.")

_ml_model = None
_ml_vectorizer = None
_ml_loaded = False
_last_metrics = None


def _three_tier(score: float) -> str:
    if score >= 0.75:
        return "Scam"
    if score >= 0.5:
        return "Suspicious"
    return "Safe"


def _train_model():
    global _ml_model, _ml_vectorizer, _last_metrics

    texts = [t for t, _ in TRAINING_DATA]
    labels = [y for _, y in TRAINING_DATA]

    _ml_vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_features=2000,
        sublinear_tf=True,
    )
    X = _ml_vectorizer.fit_transform(texts)

    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X, labels)

    try:
        cv_scores = cross_val_score(rf, X, labels, cv=5, scoring="accuracy")
        cv_accuracy = float(np.mean(cv_scores))
        cv_std = float(np.std(cv_scores))
    except Exception as e:
        print(f"[ML] Cross-validation failed: {e}")
        cv_accuracy = None
        cv_std = None

    _ml_model = rf
    joblib.dump(_ml_model, MODEL_PATH)
    joblib.dump(_ml_vectorizer, VECTORIZER_PATH)

    _last_metrics = {
        "accuracy": cv_accuracy,
        "accuracy_std": cv_std,
        "samples": len(texts),
        "cv_folds": 5,
        "model": "RandomForestClassifier",
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(_last_metrics, f)
    print(f"[ML] Trained on {len(texts)} samples. CV accuracy: {cv_accuracy}")


def _load_or_train():
    global _ml_model, _ml_vectorizer, _ml_loaded, _last_metrics
    if _ml_loaded:
        return _ml_model is not None
    _ml_loaded = True
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            _ml_model = joblib.load(MODEL_PATH)
            _ml_vectorizer = joblib.load(VECTORIZER_PATH)
            if os.path.exists(METRICS_PATH):
                with open(METRICS_PATH) as f:
                    _last_metrics = json.load(f)
            print(f"[ML] Loaded model from {MODEL_PATH}")
        else:
            _train_model()
    except Exception as e:
        print(f"[ML] Load failed: {e}")
        _ml_model = None
        _ml_vectorizer = None
    return _ml_model is not None


def retrain():
    global _ml_loaded
    _ml_loaded = False
    _train_model()
    _ml_loaded = True
    return _last_metrics


def get_metrics():
    return _last_metrics or {}


def _ml_predict(text):
    if not _load_or_train():
        return None, "ml unavailable"
    try:
        vec = _ml_vectorizer.transform([text])
        if vec.nnz == 0:
            return None, "no known tokens matched"
        proba = _ml_model.predict_proba(vec)[0]
        classes = list(_ml_model.classes_)
        score = float(proba[classes.index(1)]) if 1 in classes else float(proba[-1])
        return score, "ml scored"
    except Exception as e:
        print(f"[ML] prediction failed: {e}")
        return None, f"ml error: {e}"


def _gemini_predict(text):
    if not _gemini_client:
        return None
    try:
        prompt = f"""You are an elite cybersecurity AI analyzing SMS for Mobile Money (MoMo) fraud in Rwanda.
The text may be in Kinyarwanda, English, or French.
Return ONLY a raw JSON dictionary, no markdown, no prose.
Required format:
{{"fraud_score": 0.95, "classification_tag": "Scam", "suspicious_keywords": ["word1"]}}

IMPORTANT: classification_tag MUST be exactly "Safe", "Suspicious", or "Scam".

SMS Text: "{text}"
"""
        response = _gemini_client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=prompt,
        )
        m = re.search(r"\{.*\}", response.text, re.DOTALL)
        if not m:
            return None
        data = json.loads(m.group(0))
        score = float(data.get("fraud_score", 0.0))
        return {
            "fraud_score": score,
            "classification_tag": _three_tier(score),
            "suspicious_keywords": data.get("suspicious_keywords", []),
        }
    except Exception as e:
        print(f"[ML] Gemini error: {e}")
        return None


def predict_sms(text: str) -> dict:
    ml_score, reason = _ml_predict(text)

    if ml_score is not None:
        if ml_score < CONFIDENCE_LOW or ml_score > CONFIDENCE_HIGH:
            return {
                "fraud_score": round(ml_score, 4),
                "classification_tag": _three_tier(ml_score),
                "suspicious_keywords": [],
                "engine": "ml",
            }
        gem = _gemini_predict(text)
        if gem:
            gem["engine"] = "gemini"
            return gem
        return {
            "fraud_score": round(ml_score, 4),
            "classification_tag": _three_tier(ml_score),
            "suspicious_keywords": [],
            "engine": "ml",
        }

    gem = _gemini_predict(text)
    if gem:
        gem["engine"] = "gemini"
        return gem

    return {
        "fraud_score": 0.05,
        "classification_tag": "Safe",
        "suspicious_keywords": [],
        "engine": "fallback",
    }