from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.audit import log_action
from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.deps import client_ip, get_current_user
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if payload.role not in ("analyst", "admin"):
        raise HTTPException(status_code=400, detail="role must be 'analyst' or 'admin'")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token, expires_in = create_access_token(user.user_id, user.role, {"email": user.email})
    log_action(
        db,
        actor=user,
        action="register",
        target=user.email,
        detail=f"Registered as {user.role}",
        ip_address=client_ip(request),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": user.to_dict(),
    }


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token, expires_in = create_access_token(user.user_id, user.role, {"email": user.email})
    log_action(db, actor=user, action="login", target=user.email, ip_address=client_ip(request))
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": user.to_dict(),
    }


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user.to_dict()