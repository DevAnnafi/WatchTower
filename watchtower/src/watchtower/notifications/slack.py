import os
import httpx
from .base import Notification

def send(n: Notification, webhook_env="WATCHTOWER_SLACK_WEBHOOK"):
    url = os.getenv(webhook_env)
    if not url:
        raise RuntimeError(f"Missing environment variable: {webhook_env}")
    r = httpx.post(url, json={"text": f"*{n.title}*\n{n.body}\n{n.url}"}, timeout=15)
    r.raise_for_status()
