import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def generate_recovery_plan(
        incident_type: str,
        profile_data: Dict[str, Any],
        assessment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates a personalized recovery plan.
        Uses OpenAI if OPENAI_API_KEY is configured, otherwise falls back to a robust rule engine.
        """
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                prompt = (
                    f"Generate a concise recovery checklist for incident: {incident_type}.\n"
                    f"User Profile: {profile_data}\n"
                    f"Assessment: {assessment_data}\n"
                    "Respond with priority actions as bullet points and brief advice."
                )
                response = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are RecoveryLink AI assistant giving non-password digital recovery guidance."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                content = response.choices[0].message.content
                return {
                    "provider": "openai",
                    "plan": content
                }
            except Exception as e:
                logger.warning(f"OpenAI call failed ({e}). Falling back to rule engine.")

        # Fallback Rule Engine
        actions: List[str] = []

        has_contact = bool(profile_data.get("recovery_contact")) or assessment_data.get("recovery_contact_ready", False)
        has_email = bool(profile_data.get("recovery_email")) or assessment_data.get("recovery_email_ready", False)
        has_backup = profile_data.get("backup_status", False) or assessment_data.get("backup_ready", False)

        actions.append("1. Contact telecom operator to freeze SIM & request replacement.")

        if has_email:
            email = profile_data.get("recovery_email") or "stored recovery email"
            actions.append(f"2. Secure primary accounts using {email}.")
        else:
            actions.append("2. Access email provider recovery page from a trusted browser.")

        if has_contact:
            contact = profile_data.get("recovery_contact") or "trusted contact"
            actions.append(f"3. Reach out to {contact} to coordinate verification.")

        if has_backup:
            actions.append("4. Restore cloud/device backup onto replacement device.")
        else:
            actions.append("4. Verify cloud services (Google/iCloud) for remaining synced data.")

        actions.append("Note: RecoveryLink never bypasses security or asks for passwords.")

        plan_text = "\n".join(actions)
        return {
            "provider": "rule_engine",
            "plan": plan_text
        }
