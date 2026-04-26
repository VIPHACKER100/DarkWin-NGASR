import re

def scrub_pii(text: str) -> str:
    """
    Removes PII (emails, phone numbers, IP addresses) from reports.
    """
    # Simple patterns
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_REDACTED]', text)
    text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP_REDACTED]', text)
    return text
