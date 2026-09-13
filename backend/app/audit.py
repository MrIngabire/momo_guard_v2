from sqlalchemy.orm import Session
from app.models import AuditLog, User


def log_action(
    db: Session,
    *,
    actor: User | None,
    action: str,
    target: str | None = None,
    detail: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_id=actor.user_id if actor else None,
        actor_email=actor.email if actor else None,
        action=action,
        target=target,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry