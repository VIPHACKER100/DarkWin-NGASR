import httpx
from typing import Dict
from integrations.api_utils import APIError
from core.logging_system import get_logger

logger = get_logger("Slack.Notifications")

def send_slack_notification(message: str, config: Dict) -> None:
    """
    Sends a notification to a Slack webhook with error handling and logging.
    """
    webhook_url = config.get("notifications", {}).get("slack_webhook", "")
    if not webhook_url:
        logger.error("Slack webhook URL not configured.")
        raise APIError("Slack webhook URL not configured.")

    try:
        response = httpx.post(webhook_url, json={"text": message}, timeout=10.0)
        if response.status_code != 200:
            logger.error(f"Slack notification failed: {response.status_code} {response.text}")
            raise APIError(f"Slack notification failed: {response.status_code}")
        logger.info("Slack notification sent successfully.")
    except httpx.RequestError as e:
        logger.error(f"Slack notification request error: {e}")
        raise APIError(f"Slack notification request error: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error sending Slack notification: {e}")
        raise APIError(f"Unexpected error sending Slack notification: {e}")
