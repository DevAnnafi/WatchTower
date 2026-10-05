import os
import smtplib
from email.message import EmailMessage
from .base import Notification

def send(n: Notification, cfg: dict):
    def env(key):
        name = cfg[key]
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing environment variable: {name}")
        return value
    host = env("host_env")
    port = int(os.getenv(cfg["port_env"], "587"))
    user = env("user_env")
    password = env("password_env")
    sender = env("from_env")
    recipient = env("to_env")
    msg = EmailMessage()
    msg["Subject"] = n.title
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(f"{n.body}\n\n{n.url}")
    with smtplib.SMTP(host, port, timeout=20) as smtp:
        if cfg.get("starttls", True): smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
