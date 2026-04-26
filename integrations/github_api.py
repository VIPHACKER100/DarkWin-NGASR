import httpx
from core.config_manager import get_config

config = get_config()

def search_code(query: str) -> dict:
    """
    Searches GitHub for potential leaked secrets or relevant code.
    """
    token = config.integrations.get('github_token')
    if not token:
        return {"error": "GITHUB_TOKEN not configured"}

    url = f"https://api.github.com/search/code?q={query}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "total_count": data.get("total_count", 0),
                    "items": [{"repository": item["repository"]["full_name"], "html_url": item["html_url"]} for item in data.get("items", [])[:5]]
                }
            else:
                return {"error": f"GitHub API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
