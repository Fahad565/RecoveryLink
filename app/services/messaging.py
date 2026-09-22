import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)

class MessagingService:
    def __init__(self):
        self.username = settings.AT_USERNAME
        self.api_key = settings.AT_API_KEY
        self.sender_id = settings.AT_SENDER_ID
        self.at_client = None

        if self.username and self.api_key and self.api_key != "sandbox_key":
            try:
                import africastalking
                africastalking.initialize(self.username, self.api_key)
                self.at_client = africastalking.SMS
            except Exception as e:
                logger.warning(f"Failed to initialize Africa's Talking SDK: {e}")

    def send_sms(self, recipients: List[str], message: str) -> Dict[str, Any]:
        """
        Sends SMS via Africa's Talking or returns mock result if SDK is unavailable or in sandbox test.
        """
        if self.at_client:
            try:
                kwargs = {
                    "message": message,
                    "recipients": recipients
                }
                if self.sender_id and self.username != "sandbox":
                    kwargs["sender_id"] = self.sender_id

                response = self.at_client.send(**kwargs)
                logger.info(f"SMS sent successfully via AT: {response}")
                return {"status": "success", "response": response}
            except Exception as e:
                logger.error(f"AT SMS sending error: {e}")
                return {"status": "error", "error": str(e), "mock": True}

        # Mock / Fallback mode
        logger.info(f"[MOCK SMS] Sent to {recipients}: {message}")
        return {
            "status": "success",
            "mock": True,
            "recipients": recipients,
            "message": message
        }

messaging_service = MessagingService()
