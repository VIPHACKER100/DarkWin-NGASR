import httpx
from core.config_manager import get_config

config = get_config()

def get_domain_report(domain: str) -> dict:
    """
    Queries VirusTotal for a domain report.
    """
    api_key = config.integrations.get('vt_api_key')
    if not api_key:
        return {"error": "VT_API_KEY not configured"}

    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": api_key}
    
    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json().get('data', {}).get('attributes', {})
                return {
                    "domain": domain,
                    "reputation": data.get('reputation', 0),
                    "last_analysis_stats": data.get('last_analysis_stats', {})
                }
            else:
                return {"error": f"VirusTotal API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
