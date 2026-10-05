import os
import httpx
from .base import Notification

def send(n: Notification, token_env="WATCHTOWER_TELEGRAM_BOT_TOKEN", chat_env="WATCHTOWER_TELEGRAM_CHAT_ID"):
    token = os.getenv(token_env); chat_id = os.getenv(chat_env)
    if not token: raise RuntimeError(f"Missing environment variable: {token_env}")
    if not chat_id: raise RuntimeError(f"Missing environment variable: {chat_env}")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = httpx.post(url, json={"chat_id": chat_id, "text": f"{n.title}\n\n{n.body}\n\n{n.url}"[:4000]}, timeout=15)
    r.raise_for_status()
