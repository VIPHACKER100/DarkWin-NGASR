"""Slack notification sender for DARKWIN.

Uses httpx to POST messages to a Slack webhook URL.
Raises APIError on failure so callers can handle it consistently.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Dict

from core.logging_system import get_logger
from integrations.api_utils import APIError

logger = get_logger("Slack.Notifications")


def send_slack_notification(message: str, config: Dict) -> None:
    """Send a notification to a Slack webhook.

    Args:
        message: The message content to post.
        config: Application configuration dict; must contain
            ``notifications.slack_webhook``.

    Raises:
        APIError: If the webhook URL is missing, the request fails,
            or the response status is unexpected.
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
    except httpx.HTTPStatusError as e:
        logger.critical(f"Unexpected HTTP error sending Slack notification: {e}")
        raise APIError(f"Unexpected HTTP error sending Slack notification: {e}")
