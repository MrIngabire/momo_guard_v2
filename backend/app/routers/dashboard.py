from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.ml_engine import get_metrics
from app.models import Blacklist, SmsScan, User

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    total_scans = db.query(SmsScan).count()
    total_blocked = db.query(SmsScan).filter(SmsScan.fraud_score >= 0.75).count()
    total_suspicious = (
        db.query(SmsScan)
        .filter(SmsScan.fraud_score >= 0.5, SmsScan.fraud_score < 0.75)
        .count()
    )

    recent_flagged = (
        db.query(SmsScan)
        .filter(SmsScan.fraud_score >= 0.5)
        .order_by(SmsScan.timestamp.desc())
        .limit(8)
        .all()
    )
    blacklist_items = (
        db.query(Blacklist)
        .order_by(Blacklist.report_count.desc())
        .limit(10)
        .all()
    )

    metrics = get_metrics() or {}
    model_accuracy = metrics.get("accuracy")

    return {
        "total_scans": total_scans,
        "total_blocked": total_blocked,
        "total_suspicious": total_suspicious,
        "model_accuracy": model_accuracy,
        "avg_latency_ms": 0,  # not instrumented yet
        "recent_flagged": [s.to_dict() for s in recent_flagged],
        "blacklisted_senders": [b.to_dict() for b in blacklist_items],
    }


@router.get("/scans")
def scans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    all_scans = db.query(SmsScan).order_by(SmsScan.timestamp.desc()).all()
    return {"scans": [s.to_dict() for s in all_scans]}