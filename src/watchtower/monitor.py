from __future__ import annotations

from datetime import datetime, timezone

from . import db
from .config import load_config
from .differ import digest, summary, unified
from .fetcher import FetchError, fetch
from .models import CheckResult
from .notifications import Notification, notify
from .parser import extract_text


def check_monitor(mid: int, send_notifications: bool = True) -> CheckResult:
    monitor = db.get_monitor(mid)
    if not monitor:
        raise ValueError(f"Monitor {mid} does not exist")

    cfg = load_config()
    request_cfg = cfg["request"]

    try:
        html = fetch(
            monitor.url,
            request_cfg.get("timeout_seconds", 15),
            request_cfg.get("user_agent", "Watchtower/1.0"),
        )
    except FetchError:
        attempted_at = datetime.now(timezone.utc).isoformat()

        db.update_check_failure(
            mid,
            attempted_at,
            "FETCH_ERROR",
        )

        raise

    now = datetime.now(timezone.utc)

    try:
        text = extract_text(html, monitor.selector)

    except ValueError as exc:
        # Only handle the known missing-selector condition.
        # Other parser errors should remain visible.
        if not (monitor.selector and str(exc).startswith("CSS selector matched no elements:")):
            raise

        db.update_check_failure(
            mid,
            now.isoformat(),
            "TARGET_NOT_FOUND",
        )

        latest = db.latest_version(mid)
        old_text = latest["content"] if latest else ""

        monitor = db.get_monitor(mid)

        return CheckResult(
            changed=False,
            monitor=monitor,
            old_text=old_text,
            new_text=old_text,
            diff="",
            checked_at=now,
        )

    new_hash = digest(text)

    latest = db.latest_version(mid)
    old_text = latest["content"] if latest else ""
    old_hash = latest["content_hash"] if latest else None

    changed = latest is not None and old_hash != new_hash
    diff = unified(old_text, text) if changed else ""

    if latest is None or changed:
        db.save_version(
            mid,
            text,
            new_hash,
            now.isoformat(),
        )

    if changed:
        db.save_change(
            mid,
            old_hash,
            new_hash,
            diff,
            now.isoformat(),
        )

    db.update_check(
        mid,
        now.isoformat(),
        new_hash,
        changed,
    )

    monitor = db.get_monitor(mid)

    result = CheckResult(
        changed=changed,
        monitor=monitor,
        old_text=old_text,
        new_text=text,
        diff=diff,
        checked_at=now,
    )

    if changed and send_notifications:
        body = summary(diff)

        notify(
            Notification(
                f"Watchtower: {monitor.name} changed",
                body,
                monitor.url,
            ),
            cfg,
        )

    return result
