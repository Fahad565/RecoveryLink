from fastapi import APIRouter, Form, Header, Response, Depends
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database.database import get_db
from app.services.recovery import UserService, RecoveryProfileService, AssessmentService, ReadinessEngine, RecoveryIncidentService
from app.services.ai import AIService
from app.services.messaging import messaging_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ussd", tags=["USSD"])

@router.post("")
def ussd_callback(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(""),
    networkCode: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Africa's Talking USSD HTTP POST Webhook
    Expects application/x-www-form-urlencoded
    Returns plain text starting with CON or END
    Header: at-ussd-hop-metadata
    """
    user = UserService.get_or_create_user(db, phoneNumber)
    profile = RecoveryProfileService.get_profile(db, user.id)
    latest_assessment = AssessmentService.get_latest_assessment(db, user.id)

    text_parts = text.split("*") if text else []

    response_text = ""
    hop_metadata = "MainMenu"

    # MAIN MENU
    if text == "" or (len(text_parts) >= 2 and text_parts[-1] == "0"):
        response_text = (
            "CON Welcome to RecoveryLink\n"
            "1. Safety Check\n"
            "2. My Recovery Profile\n"
            "3. Emergency Recovery\n"
            "4. Help"
        )
        hop_metadata = "MainMenu"

    # 1. SAFETY CHECK MENU
    elif text == "1" or (len(text_parts) >= 4 and text_parts[0] == "1" and text_parts[-1] == "1"):
        response_text = (
            "CON Digital Safety Check\n"
            "1. Recovery Contact\n"
            "2. Recovery Email\n"
            "3. Data Backup\n"
            "4. Recovery Plan\n"
            "5. View Score"
        )
        hop_metadata = "SafetyCheckMenu"

    elif text == "1*1":
        response_text = (
            "CON Do you have a trusted recovery contact?\n"
            "1. Yes\n"
            "2. No"
        )
        hop_metadata = "SafetyCheck_Contact"

    elif len(text_parts) == 3 and text_parts[0] == "1" and text_parts[1] == "1":
        ans = text_parts[2] == "1"
        AssessmentService.create_assessment(
            db, user.id,
            contact_ready=ans,
            email_ready=latest_assessment.recovery_email_ready if latest_assessment else False,
            backup_ready=latest_assessment.backup_ready if latest_assessment else False,
            plan_ready=latest_assessment.recovery_plan_ready if latest_assessment else False
        )
        status_str = "YES" if ans else "NO"
        response_text = f"CON Recovery Contact marked as {status_str}.\n1. Back to Safety Check\n0. Main Menu"
        hop_metadata = "SafetyCheck_Contact_Saved"

    elif text == "1*2":
        response_text = (
            "CON Do you have a recovery email setup?\n"
            "1. Yes\n"
            "2. No"
        )
        hop_metadata = "SafetyCheck_Email"

    elif len(text_parts) == 3 and text_parts[0] == "1" and text_parts[1] == "2":
        ans = text_parts[2] == "1"
        AssessmentService.create_assessment(
            db, user.id,
            contact_ready=latest_assessment.recovery_contact_ready if latest_assessment else False,
            email_ready=ans,
            backup_ready=latest_assessment.backup_ready if latest_assessment else False,
            plan_ready=latest_assessment.recovery_plan_ready if latest_assessment else False
        )
        status_str = "YES" if ans else "NO"
        response_text = f"CON Recovery Email marked as {status_str}.\n1. Back to Safety Check\n0. Main Menu"
        hop_metadata = "SafetyCheck_Email_Saved"

    elif text == "1*3":
        response_text = (
            "CON Have you backed up your data?\n"
            "1. Yes\n"
            "2. No"
        )
        hop_metadata = "SafetyCheck_Backup"

    elif len(text_parts) == 3 and text_parts[0] == "1" and text_parts[1] == "3":
        ans = text_parts[2] == "1"
        AssessmentService.create_assessment(
            db, user.id,
            contact_ready=latest_assessment.recovery_contact_ready if latest_assessment else False,
            email_ready=latest_assessment.recovery_email_ready if latest_assessment else False,
            backup_ready=ans,
            plan_ready=latest_assessment.recovery_plan_ready if latest_assessment else False
        )
        status_str = "YES" if ans else "NO"
        response_text = f"CON Backup status marked as {status_str}.\n1. Back to Safety Check\n0. Main Menu"
        hop_metadata = "SafetyCheck_Backup_Saved"

    elif text == "1*4":
        response_text = (
            "CON Do you have an emergency recovery plan?\n"
            "1. Yes\n"
            "2. No"
        )
        hop_metadata = "SafetyCheck_Plan"

    elif len(text_parts) == 3 and text_parts[0] == "1" and text_parts[1] == "4":
        ans = text_parts[2] == "1"
        AssessmentService.create_assessment(
            db, user.id,
            contact_ready=latest_assessment.recovery_contact_ready if latest_assessment else False,
            email_ready=latest_assessment.recovery_email_ready if latest_assessment else False,
            backup_ready=latest_assessment.backup_ready if latest_assessment else False,
            plan_ready=ans
        )
        status_str = "YES" if ans else "NO"
        response_text = f"CON Emergency Plan marked as {status_str}.\n1. Back to Safety Check\n0. Main Menu"
        hop_metadata = "SafetyCheck_Plan_Saved"

    elif text == "1*5":
        current_assessment = AssessmentService.get_latest_assessment(db, user.id)
        c_ready = current_assessment.recovery_contact_ready if current_assessment else False
        e_ready = current_assessment.recovery_email_ready if current_assessment else False
        b_ready = current_assessment.backup_ready if current_assessment else False
        p_ready = current_assessment.recovery_plan_ready if current_assessment else False

        score, advice = ReadinessEngine.calculate_score(c_ready, e_ready, b_ready, p_ready)

        response_text = (
            f"END Digital Readiness: {score}/100\n"
            f"Contact: {'✓' if c_ready else '✗'} | Email: {'✓' if e_ready else '✗'}\n"
            f"Backup: {'✓' if b_ready else '✗'} | Plan: {'✓' if p_ready else '✗'}\n"
            f"{advice}"
        )
        hop_metadata = "SafetyCheck_ViewScore"

        # Trigger SMS summary
        sms_msg = f"RecoveryLink Score: {score}/100. {advice} Keep your recovery profile updated!"
        messaging_service.send_sms([phoneNumber], sms_msg)

    # 2. RECOVERY PROFILE MENU
    elif text == "2":
        contact_display = profile.recovery_contact if (profile and profile.recovery_contact) else "Not set"
        email_display = profile.recovery_email if (profile and profile.recovery_email) else "Not set"
        response_text = (
            f"CON Recovery Profile\n"
            f"Contact: {contact_display}\n"
            f"Email: {email_display}\n"
            f"1. Set Trusted Contact\n"
            f"2. Set Recovery Email\n"
            f"0. Main Menu"
        )
        hop_metadata = "ProfileMenu"

    elif text == "2*1":
        response_text = "CON Reply with trusted contact phone number (e.g. +254700123456):"
        hop_metadata = "Profile_SetContact_Prompt"

    elif len(text_parts) == 3 and text_parts[0] == "2" and text_parts[1] == "1":
        new_contact = text_parts[2]
        RecoveryProfileService.update_profile(db, user.id, {"recovery_contact": new_contact})
        response_text = f"END Trusted contact updated to: {new_contact}"
        hop_metadata = "Profile_SetContact_Done"

    elif text == "2*2":
        response_text = "CON Reply with recovery email address:"
        hop_metadata = "Profile_SetEmail_Prompt"

    elif len(text_parts) == 3 and text_parts[0] == "2" and text_parts[1] == "2":
        new_email = text_parts[2]
        RecoveryProfileService.update_profile(db, user.id, {"recovery_email": new_email})
        response_text = f"END Recovery email updated to: {new_email}"
        hop_metadata = "Profile_SetEmail_Done"

    # 3. EMERGENCY RECOVERY MENU
    elif text == "3":
        response_text = (
            "CON Emergency Recovery\n"
            "What happened to your phone?\n"
            "1. Phone lost\n"
            "2. Phone stolen\n"
            "3. New phone\n"
            "0. Main Menu"
        )
        hop_metadata = "EmergencyMenu"

    elif text in ["3*1", "3*2", "3*3"]:
        incident_map = {"3*1": "phone_lost", "3*2": "phone_stolen", "3*3": "new_phone"}
        incident_type = incident_map.get(text, "phone_lost")

        # 1. Create incident record
        incident = RecoveryIncidentService.create_incident(db, user.id, incident_type)

        # 2. Gather profile & assessment data for AI
        prof_dict = {
            "recovery_contact": profile.recovery_contact if profile else None,
            "recovery_email": profile.recovery_email if profile else None,
            "backup_status": profile.backup_status if profile else False
        }
        ass_dict = {
            "recovery_contact_ready": latest_assessment.recovery_contact_ready if latest_assessment else False,
            "recovery_email_ready": latest_assessment.recovery_email_ready if latest_assessment else False,
            "backup_ready": latest_assessment.backup_ready if latest_assessment else False,
            "recovery_plan_ready": latest_assessment.recovery_plan_ready if latest_assessment else False
        }

        # 3. Generate plan via AI layer
        ai_res = AIService.generate_recovery_plan(incident_type, prof_dict, ass_dict)
        recovery_plan_text = ai_res["plan"]

        # 4. Save summary and trigger SMS
        incident.recovery_plan_summary = recovery_plan_text
        incident.sms_sent = True
        db.commit()

        sms_payload = f"RecoveryLink Emergency Guidance ({incident_type}):\n{recovery_plan_text}"
        messaging_service.send_sms([phoneNumber], sms_payload)

        response_text = (
            "END Emergency recovery initiated!\n"
            "A personalized recovery plan has been sent to your phone via SMS."
        )
        hop_metadata = "EmergencyRecovery_Triggered"

    # 4. HELP MENU
    elif text == "4":
        response_text = (
            "END RecoveryLink helps you prepare for and navigate device loss.\n"
            "Never share passwords or PINs. Visit recoverylink.org for support."
        )
        hop_metadata = "HelpMenu"

    # FALLBACK / INVALID
    else:
        response_text = "END Invalid choice. Please redial the USSD code."
        hop_metadata = "InvalidInput"

    return Response(
        content=response_text,
        media_type="text/plain",
        headers={"at-ussd-hop-metadata": hop_metadata}
    )

@router.post("/notification")
def ussd_notification(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    status: str = Form(...),
    durationInMillis: Optional[str] = Form(None),
    hopsCount: Optional[int] = Form(None),
    hopsMetadata: Optional[str] = Form(None),
    input: Optional[str] = Form(None),
    lastAppResponse: Optional[str] = Form(None),
    errorMessage: Optional[str] = Form(None)
):
    """
    Africa's Talking End of Session Notification callback.
    """
    logger.info(f"USSD Session End Notification: session={sessionId}, phone={phoneNumber}, status={status}")
    return {"status": "received"}
