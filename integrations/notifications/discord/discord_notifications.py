"""Discord notification sender for DARKWIN.

Uses httpx to POST messages to a Discord webhook URL.
Raises APIError on failure so callers can handle it consistently.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Dict

from core.logging_system import get_logger
from integrations.api_utils import APIError

logger = get_logger("Discord.Notifications")


def send_discord_notification(message: str, config: Dict) -> None:
    """Send a notification to a Discord webhook.

    Args:
        message: The message content to post.
        config: Application configuration dict; must contain
            ``notifications.discord_webhook``.

    Raises:
        APIError: If the webhook URL is missing, the request fails,
            or the response status is unexpected.
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
    except httpx.HTTPStatusError as e:
        logger.critical(f"Unexpected HTTP error sending Discord notification: {e}")
        raise APIError(f"Unexpected HTTP error sending Discord notification: {e}")
