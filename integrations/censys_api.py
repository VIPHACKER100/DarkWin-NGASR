import httpx
from core.config_manager import get_config

config = get_config()

def search_host(ip: str) -> dict:
    """
    Queries Censys for information about a specific IP address.
    """
    api_id = config.integrations.get('censys_api_id')
    api_secret = config.integrations.get('censys_api_secret')
    
    if not api_id or not api_secret:
        return {"error": "CENSYS credentials not configured"}

    url = f"https://search.censys.io/api/v2/hosts/{ip}"
    try:
        with httpx.Client(timeout=10.0, auth=(api_id, api_secret)) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json().get('result', {})
                services = data.get('services', [])
                ports = [s.get('port') for s in services]
                return {
                    "ip": ip,
                    "ports": ports,
                    "services": len(services)
                }
            else:
                return {"error": f"Censys API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
