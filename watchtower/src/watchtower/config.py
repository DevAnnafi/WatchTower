from __future__ import annotations
import os
from pathlib import Path
import yaml

APP_DIR = Path(os.getenv("WATCHTOWER_HOME", Path.home() / ".watchtower"))
DB_PATH = APP_DIR / "watchtower.db"
CONFIG_PATH = APP_DIR / "config.yml"

DEFAULT_CONFIG = {
    "request": {"timeout_seconds": 15, "user_agent": "Watchtower/1.0 (+local change monitor)"},
    "scheduler": {"poll_seconds": 30},
    "notifications": {
        "terminal": {"enabled": True},
        "discord": {"enabled": False, "webhook_env": "WATCHTOWER_DISCORD_WEBHOOK"},
        "slack": {"enabled": False, "webhook_env": "WATCHTOWER_SLACK_WEBHOOK"},
        "telegram": {"enabled": False, "token_env": "WATCHTOWER_TELEGRAM_BOT_TOKEN", "chat_env": "WATCHTOWER_TELEGRAM_CHAT_ID"},
        "email": {
            "enabled": False,
            "host_env": "WATCHTOWER_SMTP_HOST",
            "port_env": "WATCHTOWER_SMTP_PORT",
            "user_env": "WATCHTOWER_SMTP_USER",
            "password_env": "WATCHTOWER_SMTP_PASSWORD",
            "from_env": "WATCHTOWER_EMAIL_FROM",
            "to_env": "WATCHTOWER_EMAIL_TO",
            "starttls": True,
        },
    },
}

def ensure_app_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    ensure_app_dir()
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False), encoding="utf-8")
        return DEFAULT_CONFIG.copy()
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    cfg = DEFAULT_CONFIG.copy()
    for key, value in raw.items():
        if isinstance(value, dict) and isinstance(cfg.get(key), dict):
            cfg[key] = {**cfg[key], **value}
        else:
            cfg[key] = value
    return cfg
