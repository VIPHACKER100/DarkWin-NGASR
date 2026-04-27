import httpx
from typing import Dict
from integrations.api_utils import APIError
from core.logging_system import get_logger

logger = get_logger("Discord.Notifications")

def send_discord_notification(message: str, config: Dict) -> None:
    """
    Sends a notification to a Discord webhook with error handling and logging.
    """
    webhook_url = config.get("notifications", {}).get("discord_webhook", "")
    if not webhook_url:
        logger.error("Discord webhook URL not configured.")
        raise APIError("Discord webhook URL not configured.")

    try:
        response = httpx.post(webhook_url, json={"content": message}, timeout=10.0)
        if response.status_code != 204:
            logger.error(f"Discord notification failed: {response.status_code} {response.text}")
            raise APIError(f"Discord notification failed: {response.status_code}")
        logger.info("Discord notification sent successfully.")
    except httpx.RequestError as e:
        logger.error(f"Discord notification request error: {e}")
        raise APIError(f"Discord notification request error: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error sending Discord notification: {e}")
        raise APIError(f"Unexpected error sending Discord notification: {e}")
