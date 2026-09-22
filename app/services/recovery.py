from sqlalchemy.orm import Session
from app.models.models import User, RecoveryProfile, RecoveryAssessment, RecoveryIncident
from app.schemas.schemas import RecoveryProfileCreate, RecoveryProfileBase
from typing import Optional, Tuple

class ReadinessEngine:
    @staticmethod
    def calculate_score(
        has_contact: bool,
        has_email: bool,
        has_backup: bool,
        has_plan: bool
    ) -> Tuple[int, str]:
        score = 0
        if has_contact:
            score += 25
        if has_email:
            score += 25
        if has_backup:
            score += 25
        if has_plan:
            score += 25

        if score >= 75:
            advice = "Excellent readiness! Your digital recovery preparedness is high."
        elif score >= 50:
            advice = "Moderate readiness. Consider setting up backups and an emergency plan."
        else:
            advice = "Low readiness. Please add a trusted contact and recovery email immediately."

        return score, advice

class UserService:
    @staticmethod
    def get_or_create_user(db: Session, phone_number: str) -> User:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.add(user)
            db.commit()
            db.refresh(user)

            # Initialize empty recovery profile
            profile = RecoveryProfile(user_id=user.id)
            db.add(profile)
            db.commit()
        return user

class RecoveryProfileService:
    @staticmethod
    def get_profile(db: Session, user_id: int) -> Optional[RecoveryProfile]:
        return db.query(RecoveryProfile).filter(RecoveryProfile.user_id == user_id).first()

    @staticmethod
    def update_profile(db: Session, user_id: int, profile_data: dict) -> RecoveryProfile:
        profile = db.query(RecoveryProfile).filter(RecoveryProfile.user_id == user_id).first()
        if not profile:
            profile = RecoveryProfile(user_id=user_id, **profile_data)
            db.add(profile)
        else:
            for key, value in profile_data.items():
                if value is not None:
                    setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
        return profile

class AssessmentService:
    @staticmethod
    def create_assessment(
        db: Session,
        user_id: int,
        contact_ready: bool,
        email_ready: bool,
        backup_ready: bool,
        plan_ready: bool
    ) -> RecoveryAssessment:
        score, _ = ReadinessEngine.calculate_score(contact_ready, email_ready, backup_ready, plan_ready)
        assessment = RecoveryAssessment(
            user_id=user_id,
            recovery_contact_ready=contact_ready,
            recovery_email_ready=email_ready,
            backup_ready=backup_ready,
            recovery_plan_ready=plan_ready,
            score=score
        )
        db.add(assessment)

        # Also update user profile flags if applicable
        profile = RecoveryProfileService.get_profile(db, user_id)
        if profile:
            profile.backup_status = backup_ready
            db.commit()

        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def get_latest_assessment(db: Session, user_id: int) -> Optional[RecoveryAssessment]:
        return db.query(RecoveryAssessment).filter(RecoveryAssessment.user_id == user_id).order_by(RecoveryAssessment.created_at.desc()).first()

class RecoveryIncidentService:
    @staticmethod
    def create_incident(db: Session, user_id: int, incident_type: str = "phone_lost") -> RecoveryIncident:
        incident = RecoveryIncident(
            user_id=user_id,
            incident_type=incident_type,
            status="active"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident
