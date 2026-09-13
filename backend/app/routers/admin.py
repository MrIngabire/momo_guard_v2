from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.audit import log_action
from app.database import get_db
from app.deps import client_ip, get_current_user, require_role
from app.ml_engine import get_metrics, retrain
from app.models import AuditLog, SmsScan, User
from app.schemas import RetrainResponse, UpdateUserRequest

router = APIRouter(prefix="/api", tags=["admin"])


# ---------- Users (admin only) ----------
@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return {"users": [u.to_dict() for u in users]}


@router.patch("/users/{user_id}")
def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    target = db.query(User).filter(User.user_id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.role is not None:
        if payload.role not in ("analyst", "admin"):
            raise HTTPException(status_code=400, detail="role must be 'analyst' or 'admin'")
        target.role = payload.role
    if payload.is_active is not None:
        target.is_active = payload.is_active

    db.commit()
    db.refresh(target)

    log_action(
        db,
        actor=admin,
        action="user_update",
        target=target.email,
        detail=f"role={payload.role} is_active={payload.is_active}",
        ip_address=client_ip(request),
    )
    return target.to_dict()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    target = db.query(User).filter(User.user_id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    email = target.email
    db.delete(target)
    db.commit()

    log_action(
        db,
        actor=admin,
        action="user_delete",
        target=email,
        ip_address=client_ip(request),
    )
    return {"message": "User deleted", "email": email}


# ---------- Metrics / health ----------
@router.get("/metrics")
def metrics(user: User = Depends(get_current_user)):
    return get_metrics()


@router.get("/health")
def health(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total_scans = db.query(SmsScan).count()
    total_users = db.query(User).count()
    return {
        "status": "ok",
        "scans": total_scans,
        "users": total_users,
        "metrics": get_metrics(),
    }


# ---------- Retrain (admin only) ----------
@router.post("/retrain", response_model=RetrainResponse)
def retrain_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    try:
        metrics = retrain()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrain failed: {e}")

    log_action(
        db,
        actor=admin,
        action="retrain",
        detail=f"accuracy={metrics.get('accuracy')} samples={metrics.get('samples')}",
        ip_address=client_ip(request),
    )

    return {
        "status": "ok",
        "accuracy": metrics.get("accuracy"),
        "samples": metrics.get("samples"),
        "message": "Model retrained successfully",
    }


# ---------- Audit logs (admin only) ----------
@router.get("/audit-logs")
def audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(min(limit, 500))
        .all()
    )
    return {"logs": [l.to_dict() for l in logs]}