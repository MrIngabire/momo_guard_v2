from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None
    role: str = "analyst"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class ScanRequest(BaseModel):
    sender: str = Field(min_length=1, max_length=64)
    text: str = Field(min_length=1, max_length=2000)


class ScanResponse(BaseModel):
    scan_id: str
    sender_id: str
    text_body: str
    language: Optional[str]
    fraud_score: float
    classification: str
    suspicious_keywords: list[str]
    engine: Optional[str]
    timestamp: datetime


class FeedbackRequest(BaseModel):
    scan_id: str
    is_false_positive: bool = False


class BlacklistRemoveRequest(BaseModel):
    blacklist_id: str


class UpdateUserRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class RetrainResponse(BaseModel):
    status: str
    accuracy: Optional[float] = None
    samples: Optional[int] = None
    message: str


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)