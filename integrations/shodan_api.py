import shodan
from core.config_manager import get_config

config = get_config()

def search_host(ip: str) -> dict:
    """
    Queries Shodan for information about a specific IP address.
    """
    if not config.integrations.get('shodan_api_key'):
        return {"error": "SHODAN_API_KEY not configured"}

    try:
        api = shodan.Shodan(config.integrations['shodan_api_key'])
        host = api.host(ip)
        
        return {
            "ip": host.get('ip_str'),
            "organization": host.get('org', 'n/a'),
            "os": host.get('os', 'n/a'),
            "ports": host.get('ports', []),
            "hostnames": host.get('hostnames', []),
            "vulns": host.get('vulns', [])
        }
    except shodan.APIError as e:
        return {"error": f"Shodan API Error: {e}"}
    except Exception as e:
        return {"error": str(e)}
