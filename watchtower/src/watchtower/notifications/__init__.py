from .base import Notification
from . import terminal, discord, email, slack, telegram

def notify(n: Notification, cfg: dict):
    nc = cfg.get("notifications", {})
    errors = []
    if nc.get("terminal", {}).get("enabled", True): terminal.send(n)
    providers = [
        ("Discord", nc.get("discord", {}), lambda c: discord.send(n, c.get("webhook_env", "WATCHTOWER_DISCORD_WEBHOOK"))),
        ("Slack", nc.get("slack", {}), lambda c: slack.send(n, c.get("webhook_env", "WATCHTOWER_SLACK_WEBHOOK"))),
        ("Telegram", nc.get("telegram", {}), lambda c: telegram.send(n, c.get("token_env", "WATCHTOWER_TELEGRAM_BOT_TOKEN"), c.get("chat_env", "WATCHTOWER_TELEGRAM_CHAT_ID"))),
        ("Email", nc.get("email", {}), lambda c: email.send(n, c)),
    ]
    for name, pcfg, sender in providers:
        if pcfg.get("enabled"):
            try: sender(pcfg)
            except Exception as e: errors.append(f"{name}: {e}")
    return errors
