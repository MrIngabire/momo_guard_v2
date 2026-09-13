import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "tbl_users"

    user_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=True)
    role = Column(String(20), nullable=False, default="analyst")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    scans = relationship(
        "SmsScan",
        back_populates="analyst",
        foreign_keys="SmsScan.analyst_id",
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="actor",
        foreign_keys="AuditLog.actor_id",
    )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


class SmsScan(Base):
    __tablename__ = "tbl_sms_scans"

    scan_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    sender_id = Column(String(50), nullable=False)
    text_body = Column(Text, nullable=False)
    language = Column(String(32), nullable=True)
    fraud_score = Column(Float, nullable=False)
    classification = Column(String(20), nullable=False)
    engine = Column(String(20), nullable=True)
    user_disputed = Column(Boolean, nullable=False, default=False)
    analyst_id = Column(UUID(as_uuid=False), ForeignKey("tbl_users.user_id"), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    analyst = relationship("User", back_populates="scans", foreign_keys=[analyst_id])

    __table_args__ = (
        Index("ix_sms_scans_timestamp", "timestamp"),
        Index("ix_sms_scans_fraud_score", "fraud_score"),
    )

    def to_dict(self):
        return {
            "scan_id": self.scan_id,
            "sender_id": self.sender_id,
            "text_body": self.text_body,
            "language": self.language,
            "fraud_score": self.fraud_score,
            "classification": self.classification,
            "engine": self.engine,
            "user_disputed": self.user_disputed,
            "analyst_id": self.analyst_id,
            "timestamp": self.timestamp.isoformat(),
        }


class Blacklist(Base):
    __tablename__ = "tbl_blacklist"

    blacklist_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    phone_number = Column(String(32), unique=True, nullable=False, index=True)
    report_count = Column(Integer, nullable=False, default=1)
    reason = Column(String(255), nullable=True)
    last_updated = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "blacklist_id": self.blacklist_id,
            "phone_number": self.phone_number,
            "report_count": self.report_count,
            "reason": self.reason,
            "last_updated": self.last_updated.isoformat(),
        }


class AuditLog(Base):
    __tablename__ = "tbl_audit_logs"

    log_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    actor_id = Column(UUID(as_uuid=False), ForeignKey("tbl_users.user_id"), nullable=True)
    actor_email = Column(String(120), nullable=True)
    action = Column(String(64), nullable=False)
    target = Column(String(255), nullable=True)
    detail = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    actor = relationship("User", back_populates="audit_logs", foreign_keys=[actor_id])

    __table_args__ = (
        Index("ix_audit_logs_timestamp", "timestamp"),
        Index("ix_audit_logs_action", "action"),
    )

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "actor_id": self.actor_id,
            "actor_email": self.actor_email,
            "action": self.action,
            "target": self.target,
            "detail": self.detail,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat(),
        }