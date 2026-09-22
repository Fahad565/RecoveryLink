from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    phone_number: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RecoveryProfileBase(BaseModel):
    recovery_contact: Optional[str] = None
    recovery_email: Optional[str] = None
    backup_status: bool = False
    recovery_codes_available: bool = False
    emergency_notes: Optional[str] = None

class RecoveryProfileCreate(RecoveryProfileBase):
    pass

class RecoveryProfileResponse(RecoveryProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RecoveryAssessmentBase(BaseModel):
    recovery_contact_ready: bool = False
    recovery_email_ready: bool = False
    backup_ready: bool = False
    recovery_plan_ready: bool = False

class RecoveryAssessmentResponse(RecoveryAssessmentBase):
    id: int
    user_id: int
    score: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RecoveryIncidentCreate(BaseModel):
    incident_type: str = "phone_lost"

class RecoveryIncidentResponse(BaseModel):
    id: int
    user_id: int
    incident_type: str
    status: str
    sms_sent: bool
    recovery_plan_summary: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
