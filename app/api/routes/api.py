from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.services.recovery import UserService, RecoveryProfileService, AssessmentService
from app.schemas.schemas import UserResponse, RecoveryProfileResponse, RecoveryProfileBase, RecoveryAssessmentResponse, RecoveryIncidentResponse
from app.models.models import RecoveryIncident

router = APIRouter(prefix="/api/v1", tags=["REST API"])

@router.get("/users/{phone_number}", response_model=UserResponse)
def get_user_by_phone(phone_number: str, db: Session = Depends(get_db)):
    user = UserService.get_or_create_user(db, phone_number)
    return user

@router.get("/profiles/{user_id}", response_model=RecoveryProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    profile = RecoveryProfileService.get_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/profiles/{user_id}", response_model=RecoveryProfileResponse)
def update_user_profile(user_id: int, profile_update: RecoveryProfileBase, db: Session = Depends(get_db)):
    profile = RecoveryProfileService.update_profile(db, user_id, profile_update.model_dump(exclude_unset=True))
    return profile

@router.get("/assessments/{user_id}", response_model=RecoveryAssessmentResponse)
def get_latest_assessment(user_id: int, db: Session = Depends(get_db)):
    assessment = AssessmentService.get_latest_assessment(db, user_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found for user")
    return assessment

@router.get("/incidents/{user_id}", response_model=List[RecoveryIncidentResponse])
def list_user_incidents(user_id: int, db: Session = Depends(get_db)):
    incidents = db.query(RecoveryIncident).filter(RecoveryIncident.user_id == user_id).all()
    return incidents
