from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    recovery_profile = relationship("RecoveryProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    assessments = relationship("RecoveryAssessment", back_populates="user", cascade="all, delete-orphan")
    incidents = relationship("RecoveryIncident", back_populates="user", cascade="all, delete-orphan")

class RecoveryProfile(Base):
    __tablename__ = "recovery_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    recovery_contact = Column(String(50), nullable=True)
    recovery_email = Column(String(100), nullable=True)
    backup_status = Column(Boolean, default=False)
    recovery_codes_available = Column(Boolean, default=False)
    emergency_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="recovery_profile")

class RecoveryAssessment(Base):
    __tablename__ = "recovery_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recovery_contact_ready = Column(Boolean, default=False)
    recovery_email_ready = Column(Boolean, default=False)
    backup_ready = Column(Boolean, default=False)
    recovery_plan_ready = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="assessments")

class RecoveryIncident(Base):
    __tablename__ = "recovery_incidents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    incident_type = Column(String(50), nullable=False) # e.g., phone_lost, phone_stolen
    status = Column(String(50), default="active") # active, resolved
    sms_sent = Column(Boolean, default=False)
    recovery_plan_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="incidents")
