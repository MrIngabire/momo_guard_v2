from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.audit import log_action
from app.database import get_db
from app.deps import client_ip, require_role
from app.models import Blacklist, User
from app.schemas import BlacklistRemoveRequest

router = APIRouter(prefix="/api/blacklist", tags=["blacklist"])


@router.get("")
def list_blacklist(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    entries = db.query(Blacklist).order_by(Blacklist.report_count.desc()).all()
    return {"blacklist": [e.to_dict() for e in entries]}


@router.post("/remove")
def remove_blacklist(
    payload: BlacklistRemoveRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    entry = db.query(Blacklist).filter(Blacklist.blacklist_id == payload.blacklist_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Blacklist entry not found")

    phone = entry.phone_number
    db.delete(entry)
    db.commit()

    log_action(
        db,
        actor=user,
        action="blacklist_remove",
        target=phone,
        ip_address=client_ip(request),
    )
    return {"message": "Blacklist entry removed", "phone_number": phone}