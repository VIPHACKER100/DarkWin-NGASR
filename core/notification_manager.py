"""DARKWIN Notification Manager

Handles outbound notifications for critical security events and 
verified findings via Discord, Slack, and Telegram webhooks.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
import json
from typing import Dict, Any, Optional
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("NotificationManager")
config = get_config()

class NotificationManager:
    """Dispatches alerts to external communication channels."""
    
    def __init__(self):
        self.webhooks = config.notifications or {}

    async def send_alert(self, title: str, message: str, severity: str = "Info"):
        """Send a notification to all configured channels."""
        payload = {
            "title": f"🚨 DARKWIN ALERT: {title}",
            "message": message,
            "severity": severity,
            "timestamp": str(httpx.utils.guess_json_utf(b"")) # Placeholder for now
        }
        
        # Discord Hook
        if self.webhooks.get("discord"):
            await self._send_discord(title, message, severity)
        
        # Slack Hook
        if self.webhooks.get("slack"):
            await self._send_slack(title, message, severity)

    async def _send_discord(self, title: str, message: str, severity: str):
        url = self.webhooks.get("discord")
        color = 0xFF0000 if severity == "Critical" else 0xFFAA00
        
        embed = {
            "title": f"DARKWIN: {title}",
            "description": message,
            "color": color,
            "footer": {"text": "Autonomous Security Researcher"}
        }
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json={"embeds": [embed]})
        except Exception as e:
            logger.error(f"Discord notification failed: {e}")

    async def _send_slack(self, title: str, message: str, severity: str):
        url = self.webhooks.get("slack")
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json={"text": f"*DARKWIN ALERT*: {title}\n{message}"})
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")

# Global instance
global_notifier = NotificationManager()
