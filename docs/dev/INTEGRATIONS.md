# DARKWIN Integration Development Guide

## Overview

DARKWIN supports external API integrations for passive reconnaissance enrichment, threat intelligence, and alerting. Integrations live in the `integrations/` directory.

## Current Integrations

| Integration | Path | Purpose |
|---|---|---|
| Shodan | `integrations/shodan_api.py` | Passive port/service enumeration |
| Censys | `integrations/censys_api.py` | Certificate and asset discovery |
| VirusTotal | `integrations/virustotal_api.py` | Domain/IP reputation and threat intel |
| GitHub | `integrations/github_api.py` | Code search, secret leak detection |
| Discord | `integrations/notifications/discord/` | Critical finding alerts |
| Slack | `integrations/notifications/slack/` | Critical finding alerts |

## Adding a New Integration

### 1. Create the integration module

```python
# integrations/my_service.py
"""MyService API integration."""

import httpx
from core.config_manager import ConfigManager

class MyServiceAPI:
    """Client for MyService security API."""

    def __init__(self, config: ConfigManager):
        self.api_key = config.get("api_keys", "my_service")
        self.base_url = "https://api.myservice.com/v1"
        self.client = httpx.Client(timeout=30)

    def search(self, query: str) -> dict:
        """Search the service for a given query."""
        response = self.client.get(
            f"{self.base_url}/search",
            headers={"Authorization": f"Bearer {self.api_key}"},
            params={"q": query},
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()
```

### 2. Register in config.yaml

```yaml
api_keys:
  my_service: "your-api-key-here"
```

### 3. Use in a scan module

```python
# modules/reconnaissance/my_recon.py
from integrations.my_service import MyServiceAPI

async def run(target, scan_id, config):
    api = MyServiceAPI(config)
    try:
        results = api.search(target)
        # Process results and return findings
        return findings
    finally:
        api.close()
```

### 4. (Optional) Add notification channel

For new notification channels (Discord/Slack style):

```python
# integrations/notifications/my_channel.py
class MyChannelNotifier:
    def send_alert(self, finding: dict):
        webhook_url = config.get("notifications", "my_channel")
        payload = self._build_payload(finding)
        httpx.post(webhook_url, json=payload)
```

Register in `config.yaml`:

```yaml
notifications:
  my_channel: "https://hooks.my-channel.com/..."
```

## Integration Patterns

### Error Handling
Always wrap API calls with try/except and log failures:

```python
try:
    result = api.search(target)
except httpx.HTTPStatusError as e:
    logger.warning(f"MyService API error: {e.response.status_code}")
    return []
except httpx.RequestError as e:
    logger.error(f"MyService connection failed: {e}")
    return []
```

### Rate Limiting
Respect API rate limits using `core/rate_limiter.py`:

```python
from core.rate_limiter import rate_limit

@rate_limit(max_per_second=5)
def api_call(query):
    return client.get(...)
```

### Caching
Cache results with `core/cache_manager.py`:

```python
from core.cache_manager import CacheManager

cache = CacheManager()
cached = cache.get(f"myservice:{target}")
if cached:
    return cached

result = api.search(target)
cache.set(f"myservice:{target}", result, ttl=3600)
return result
```

## API Key Management

- Keys are stored in `config.yaml` or `.env`
- The `darkwin config --view` command auto-masks secrets
- Never commit real keys to version control
