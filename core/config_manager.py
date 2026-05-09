import os
import yaml
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseModel):
    name: str = "DARKWIN"
    version: str = "1.0.0"
    author: str = "ARYAN AHIRWAR (VIPHACKER.100)"

class DatabaseConfig(BaseModel):
    url: str = "postgresql://darkwin:darkwin_secret@localhost:5432/darkwin"

class RedisConfig(BaseModel):
    url: str = "redis://localhost:6379/0"

class AIConfig(BaseModel):
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    local_llm_url: str = "http://localhost:11434/v1"

class ToolsConfig(BaseModel):
    nmap: str = "nmap"
    subfinder: str = "subfinder"
    httpx: str = "httpx"
    nuclei: str = "nuclei"
    ffuf: str = "ffuf"
    amass: str = "amass"
    katana: str = "katana"
    sqlmap: str = "sqlmap"
    dalfox: str = "dalfox"
    masscan: str = "masscan"

class ScansConfig(BaseModel):
    output_dir: str = "reports"
    log_dir: str = "logs"
    max_threads: int = 20
    timeout: int = 3600
    rate_limit: int = 10

class APIKeysConfig(BaseModel):
    shodan: str = ""
    censys_id: str = ""
    censys_secret: str = ""
    virustotal: str = ""
    github_token: str = ""

class ProxyConfig(BaseModel):
    proxy_file: Optional[str] = None
    proxies: list = []

class NotificationConfig(BaseModel):
    discord: Optional[str] = None
    slack: Optional[str] = None
    telegram: Optional[str] = None

class DarkwinConfig(BaseSettings):
    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    ai: AIConfig = AIConfig()
    tools: ToolsConfig = ToolsConfig()
    scans: ScansConfig = ScansConfig()
    api_keys: APIKeysConfig = APIKeysConfig()
    proxy: ProxyConfig = ProxyConfig()
    notifications: NotificationConfig = NotificationConfig()


    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore"
    )

_config: Optional[DarkwinConfig] = None

def load_config(config_path: str = "config.yaml") -> DarkwinConfig:
    global _config
    if _config:
        return _config

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            _config = DarkwinConfig(**data)
    else:
        _config = DarkwinConfig()
    
    return _config

def get_config() -> DarkwinConfig:
    return load_config()

def validate_config():
    config = get_config()
    # Perform basic validation
    if not config.database.url:
        raise ValueError("Database URL is missing in configuration.")
    # Add more validations as needed
