from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth import decode_token
from app.database import get_db
from app.models import User

# Kept for OAuth2 password flow (form-based login) — unused for now but harmless
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# This is the one that gives you the "paste your token" box in Swagger
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    token_fallback: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Accepts the JWT from either:
      - Authorization: Bearer <token>   (the normal path, from HTTPBearer)
      - the OAuth2 form field            (fallback, unused)
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif token_fallback:
        token = token_fallback

    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc
    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exc

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exc

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.is_active:
        raise credentials_exc
    return user


def require_role(*allowed_roles: str):
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role in {allowed_roles}; you are '{user.role}'",
            )
        return user
    return _checker


def client_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None