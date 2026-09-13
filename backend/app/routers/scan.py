from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.audit import log_action
from app.database import get_db
from app.deps import client_ip, get_current_user
from app.ml_engine import predict_sms
from app.models import Blacklist, SmsScan, User
from app.schemas import FeedbackRequest, ScanRequest, ScanResponse

router = APIRouter(prefix="/api", tags=["scan"])


def _detect_language(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["mtn", "rwf", "kanda", "kwakira", "momo"]):
        return "Mixed/Kinyarwanda"
    if any(w in t for w in ["cliquez", "confirmer", "identite", "bienvenue"]):
        return "French"
    if any(w in t for w in ["your", "account", "bundle", "service"]):
        return "English"
    return "unknown"


def _run_scan(db: Session, sender: str, text: str, analyst_id: str | None):
    prediction = predict_sms(text)
    language = _detect_language(text)

    scan_row = SmsScan(
        sender_id=sender,
        text_body=text,
        language=language,
        fraud_score=prediction["fraud_score"],
        classification=prediction["classification_tag"],
        engine=prediction.get("engine"),
        analyst_id=analyst_id,
    )
    db.add(scan_row)
    db.commit()
    db.refresh(scan_row)

    return {
        "scan_id": scan_row.scan_id,
        "sender_id": scan_row.sender_id,
        "text_body": scan_row.text_body,
        "language": scan_row.language,
        "fraud_score": scan_row.fraud_score,
        "classification": scan_row.classification,
        "suspicious_keywords": prediction.get("suspicious_keywords", []),
        "engine": scan_row.engine,
        "timestamp": scan_row.timestamp,
    }


# ---------- Authenticated scan (dashboard / web) ----------
@router.post("/scan", response_model=ScanResponse)
def scan(
    payload: ScanRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return _run_scan(db, payload.sender, payload.text, user.user_id)


# ---------- Public scan (mobile app, no auth) ----------
@router.post("/scan-public", response_model=ScanResponse)
def scan_public(
    payload: ScanRequest,
    db: Session = Depends(get_db),
):
    """
    Public endpoint used by the native Android client.
    No JWT required — the phone posts { sender, text } and gets
    a classification back. The scan is still logged with analyst_id=None.
    """
    return _run_scan(db, payload.sender, payload.text, None)


@router.post("/feedback")
def feedback(
    payload: FeedbackRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    scan_row = db.query(SmsScan).filter(SmsScan.scan_id == payload.scan_id).first()
    if not scan_row:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan_row.user_disputed = bool(payload.is_false_positive)
    db.commit()

    blacklisted = False
    if not payload.is_false_positive and scan_row.sender_id:
        entry = (
            db.query(Blacklist)
            .filter(Blacklist.phone_number == scan_row.sender_id)
            .first()
        )
        if entry:
            entry.report_count += 1
        else:
            entry = Blacklist(
                phone_number=scan_row.sender_id,
                report_count=1,
                reason="Confirmed scam via feedback",
            )
            db.add(entry)
        db.commit()
        blacklisted = True

    log_action(
        db,
        actor=user,
        action="feedback",
        target=scan_row.scan_id,
        detail=f"is_false_positive={payload.is_false_positive}",
        ip_address=client_ip(request),
    )

    return {
        "message": "Feedback recorded",
        "scan_id": scan_row.scan_id,
        "user_disputed": scan_row.user_disputed,
        "blacklisted": blacklisted,
    }