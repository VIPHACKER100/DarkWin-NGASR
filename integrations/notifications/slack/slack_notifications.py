import httpx

def send_slack_notification(message: str, config: dict):
    """
    Sends a notification to a Slack webhook.
    """
    webhook_url = config.get("notifications", {}).get("slack_webhook", "")
    if not webhook_url:
        return
        
    try:
        httpx.post(webhook_url, json={"text": message})
    except Exception:
        pass
