import httpx

def send_discord_notification(message: str, config: dict):
    """
    Sends a notification to a Discord webhook.
    """
    webhook_url = config.get("notifications", {}).get("discord_webhook", "")
    if not webhook_url:
        return
        
    try:
        httpx.post(webhook_url, json={"content": message})
    except Exception:
        pass
