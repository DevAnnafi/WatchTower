import os

import httpx

from .base import Notification


def send(n: Notification, webhook_env="WATCHTOWER_DISCORD_WEBHOOK"):
    url = os.getenv(webhook_env)
    if not url:
        raise RuntimeError(f"Missing environment variable: {webhook_env}")
    content = f"**{n.title}**\n{n.body}\n{n.url}"
    response = httpx.post(url, json={"content": content[:1900]}, timeout=15)
    response.raise_for_status()
