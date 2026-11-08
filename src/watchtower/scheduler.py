from __future__ import annotations

import time
from datetime import datetime, timezone

from . import db
from .config import load_config
from .monitor import check_monitor


def _due(m, now):
    """Determine whether a monitor is due for another attempt."""

    last_attempt = m.last_attempted or m.last_checked

    if not last_attempt:
        return True

    last = datetime.fromisoformat(last_attempt)

    return (
        now - last
    ).total_seconds() >= m.interval_minutes * 60


def run_forever():
    cfg = load_config()
    poll = int(cfg.get("scheduler", {}).get("poll_seconds", 30))

    while True:
        now = datetime.now(timezone.utc)

        for m in db.list_monitors():
            if not m.enabled or not _due(m, now):
                continue

            try:
                result = check_monitor(m.id)

                if result.monitor.status == "TARGET_NOT_FOUND":
                    print(
                        f"[{m.id}] {m.name}: "
                        "TARGET_NOT_FOUND "
                        f"(selector: {m.selector})"
                    )

            except Exception as exc:  # noqa: BLE001
                print(f"[{m.id}] {m.name}: {exc}")

        time.sleep(poll)
