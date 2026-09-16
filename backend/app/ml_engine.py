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
from sqlalchemy.orm import Session

from app.config import settings
from app.training_data import TRAINING_DATA
from app.trusted_senders import (
    is_trusted,
    TRUST_SCORE_CAP,
    BLACKLIST_SCORE_FLOOR,
    TRUST_BYPASS_CEILING,
)

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "rf_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "metrics.json")

# --- Trust thresholds --------------------------------------------------------
CONFIDENCE_LOW = 0.35
CONFIDENCE_HIGH = 0.65
MIN_TOKEN_MATCHES = 3

# --- Receipt pattern bypass --------------------------------------------------
# If a message matches one of these patterns, it's structurally an MTN MoMo
# receipt and doesn't need ML analysis. Scammers cannot fabricate a real FT Id.
RECEIPT_PATTERNS = [
    r"FT Id:\s*\d+",
    r"Balance:\s*\d+\s*RWF",
    r"Fee:\s*\d+\s*RWF",
    r"\*165\*S\*",
    r"transferred to .+\(\d+\)\s+at\s+\d{4}-\d{2}-\d{2}",
    r"received \d+\s*RWF from .+\s+at\s+\d{4}-\d{2}-\d{2}",
]
_RECEIPT_REGEX = re.compile("|".join(RECEIPT_PATTERNS), re.IGNORECASE)


def _looks_like_receipt(text: str) -> bool:
    return bool(_RECEIPT_REGEX.search(text))


# --- Gemini client -----------------------------------------------------------
_gemini_client = None
if settings.GEMINI_API_KEY:
    _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    print("[ML] Gemini client initialised.")
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
        "vocabulary_size": len(_ml_vectorizer.vocabulary_),
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


def _ml_predict(text: str):
    if not _load_or_train():
        return None, "ml unavailable"
    try:
        vec = _ml_vectorizer.transform([text])
        if vec.nnz == 0:
            return None, "no known tokens matched (unseen vocabulary)"
        if vec.nnz < MIN_TOKEN_MATCHES:
            return None, f"only {vec.nnz} token match(es) — too low signal"
        proba = _ml_model.predict_proba(vec)[0]
        classes = list(_ml_model.classes_)
        score = float(proba[classes.index(1)]) if 1 in classes else float(proba[-1])
        return score, f"ml scored (nnz={vec.nnz})"
    except Exception as e:
        print(f"[ML] prediction failed: {e}")
        return None, f"ml error: {e}"


def _gemini_predict(text: str, sender: str | None = None):
    if not _gemini_client:
        return None
    try:
        sender_line = f'From: "{sender}"\n' if sender else ""
        prompt = f"""You are an elite cybersecurity AI analyzing SMS for Mobile Money (MoMo) fraud in Rwanda.
The text may be in Kinyarwanda, English, or French.
Return ONLY a raw JSON dictionary, no markdown, no prose.
Required format:
{{"fraud_score": 0.95, "classification_tag": "Scam", "suspicious_keywords": ["word1"]}}

IMPORTANT: classification_tag MUST be exactly "Safe", "Suspicious", or "Scam".
Note: "M-Money", "MTN", "MTN MoMo" are OFFICIAL MTN Rwanda MoMo sender IDs and their
messages are legitimate transaction receipts unless the content is clearly suspicious.

{sender_line}SMS Text: "{text}"
"""
        response = _gemini_client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=prompt,
        )
        m = re.search(r"\{.*\}", response.text, re.DOTALL)
        if not m:
            print("[ML] Gemini returned no parsable JSON.")
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


def _apply_sender_trust(
    result: dict,
    sender: str | None,
    db: Session | None = None,
) -> dict:
    """
    Adjust the ML/Gemini result based on the sender ID.

    - Trusted MTN sender  → cap score at TRUST_SCORE_CAP (unless raw ≥ 0.75)
    - Blacklisted sender  → raise score to at least BLACKLIST_SCORE_FLOOR
    """
    if not sender:
        return result

    score = result["fraud_score"]

    # --- Trusted sender ---
    if is_trusted(sender):
        if score < TRUST_BYPASS_CEILING:
            capped = min(score, TRUST_SCORE_CAP)
            result["fraud_score"] = round(capped, 4)
            result["classification_tag"] = "Safe"
            result["engine"] = f"{result.get('engine', 'ml')}+trusted"
            print(
                f"[ML] Trusted sender '{sender}' — capped {score:.2f} → {capped:.2f}"
            )
        else:
            print(
                f"[ML] Trusted sender '{sender}' but score {score:.2f} ≥ "
                f"{TRUST_BYPASS_CEILING} — leaving decision to ML/Gemini."
            )
        return result

    # --- Blacklisted sender ---
    if db is not None:
        try:
            from app.models import Blacklist
            entry = (
                db.query(Blacklist)
                .filter(Blacklist.phone_number == sender)
                .first()
            )
            if entry and score < BLACKLIST_SCORE_FLOOR:
                boosted = max(score, BLACKLIST_SCORE_FLOOR)
                result["fraud_score"] = round(boosted, 4)
                result["classification_tag"] = _three_tier(boosted)
                result["engine"] = f"{result.get('engine', 'ml')}+blacklist"
                print(
                    f"[ML] Blacklisted sender '{sender}' — boosted "
                    f"{score:.2f} → {boosted:.2f}"
                )
        except Exception as e:
            print(f"[ML] Blacklist check failed: {e}")

    return result


def predict_sms(
    text: str,
    sender: str | None = None,
    db: Session | None = None,
) -> dict:
    """
    Main entry point.
    Returns { fraud_score, classification_tag, suspicious_keywords, engine }.
    engine values: 'rule', 'ml', 'gemini', 'fallback', plus '+trusted' / '+blacklist' suffixes.
    """

    # --- Fast path 1: sender is a trusted MTN shortcode ---
    if sender and is_trusted(sender):
        # Still scan for obvious scam signals (asking for PIN, external links)
        suspicious = _has_scam_markers(text)
        if not suspicious:
            print(f"[ML] Trusted sender '{sender}' with clean content — Safe (trusted).")
            return {
                "fraud_score": 0.02,
                "classification_tag": "Safe",
                "suspicious_keywords": [],
                "engine": "trusted",
            }
        else:
            print(
                f"[ML] Trusted sender '{sender}' but scam markers present — running full pipeline."
            )

    # --- Fast path 2: receipt-shaped message ---
    if _looks_like_receipt(text):
        print("[ML] Receipt pattern detected — Safe (rule).")
        return {
            "fraud_score": 0.02,
            "classification_tag": "Safe",
            "suspicious_keywords": [],
            "engine": "rule",
        }

    # --- Standard ML → Gemini pipeline ---
    ml_score, reason = _ml_predict(text)

    if ml_score is not None:
        if ml_score < CONFIDENCE_LOW or ml_score > CONFIDENCE_HIGH:
            print(f"[ML] ML answered {ml_score:.2f} ({reason}) — high confidence.")
            result = {
                "fraud_score": round(ml_score, 4),
                "classification_tag": _three_tier(ml_score),
                "suspicious_keywords": [],
                "engine": "ml",
            }
            return _apply_sender_trust(result, sender, db)

        print(f"[ML] ML score {ml_score:.2f} is ambiguous — consulting Gemini.")
        gem = _gemini_predict(text, sender)
        if gem:
            gem["engine"] = "gemini"
            return _apply_sender_trust(gem, sender, db)
        print("[ML] Gemini failed; falling back to ambiguous ML answer.")
        result = {
            "fraud_score": round(ml_score, 4),
            "classification_tag": _three_tier(ml_score),
            "suspicious_keywords": [],
            "engine": "ml",
        }
        return _apply_sender_trust(result, sender, db)

    print(f"[ML] ML skipped ({reason}) — using Gemini directly.")
    gem = _gemini_predict(text, sender)
    if gem:
        gem["engine"] = "gemini"
        return _apply_sender_trust(gem, sender, db)

    print("[ML] All engines failed. Returning safe default.")
    return {
        "fraud_score": 0.05,
        "classification_tag": "Safe",
        "suspicious_keywords": [],
        "engine": "fallback",
    }


# --- Scam marker detection (used for trusted senders) -----------------------
_SCAM_MARKER_PATTERNS = [
    r"\bPIN\b",
    r"\bpassword\b",
    r"https?://(?!.*mtn\.rw)",
    r"bit\.ly",
    r"cliquez",
    r"click here",
    r"kanda\s+kuri",
    r"verify your (account|identity)",
    r"confirm your (account|identity)",
    r"\burgent\b",
    r"\bcompromised\b",
]
_SCAM_MARKER_REGEX = re.compile("|".join(_SCAM_MARKER_PATTERNS), re.IGNORECASE)


def _has_scam_markers(text: str) -> bool:
    return bool(_SCAM_MARKER_REGEX.search(text))