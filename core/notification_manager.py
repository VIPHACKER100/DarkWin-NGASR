"""DARKWIN Notification Manager

Handles outbound notifications for critical security events and 
verified findings via Discord, Slack, and Telegram webhooks.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

"""
DARKWIN Notification Manager

Handles outbound notifications for critical security events and
verified findings via Discord and Slack webhooks.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: MIT
"""

import httpx
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("NotificationManager")
config = get_config()

class NotificationManager:
    """Dispatches alerts to external communication channels."""

    def __init__(self) -> None:
        # Support both dict and Pydantic model for backward compatibility
        if hasattr(config.notifications, "model_dump"):
            self.webhooks: Dict[str, Any] = config.notifications.model_dump()
        elif hasattr(config.notifications, "dict"):
            self.webhooks = config.notifications.dict()
        else:
            self.webhooks = config.notifications or {}

    async def send_alert(self, title: str, message: str, severity: str = "Info") -> None:
        """Send a notification to all configured channels.

        Args:
            title: Alert title.
            message: Alert body text.
            severity: Severity level (Critical, High, Medium, Low, Info).
        """
        if self.webhooks.get("discord"):
            await self._send_discord(title, message, severity)

        if self.webhooks.get("slack"):
            await self._send_slack(title, message, severity)

    async def _send_discord(self, title: str, message: str, severity: str) -> None:
        """Send a Discord embed notification via webhook."""
        url = self.webhooks.get("discord")
        color = 0xFF0000 if severity == "Critical" else 0xFFAA00
        embed: Dict[str, Any] = {
            "title": f"DARKWIN: {title}",
            "description": message,
            "color": color,
            "footer": {"text": "Autonomous Security Researcher"}
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json={"embeds": [embed]})
        except httpx.RequestError as e:
            logger.error(f"Discord notification failed: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Discord notification timeout: {e}")

    async def _send_slack(self, title: str, message: str, severity: str) -> None:
        """Send a Slack message notification via webhook."""
        url = self.webhooks.get("slack")
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json={"text": f"*DARKWIN ALERT*: {title}\n{message}"})
        except httpx.RequestError as e:
            logger.error(f"Slack notification failed: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Slack notification timeout: {e}")

# Global instance
global_notifier: NotificationManager = NotificationManager()
