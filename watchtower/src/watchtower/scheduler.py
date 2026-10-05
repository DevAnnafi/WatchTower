from __future__ import annotations

import time
from datetime import datetime, timezone

from . import db
from .config import load_config
from .monitor import check_monitor


def _due(m, now):
    if not m.last_checked:
        return True

    last = datetime.fromisoformat(m.last_checked)
    return (now - last).total_seconds() >= m.interval_minutes * 60


def run_forever():
    cfg = load_config()
    poll = int(cfg.get("scheduler", {}).get("poll_seconds", 30))

    while True:
        now = datetime.now(timezone.utc)

        for m in db.list_monitors():
            if m.enabled and _due(m, now):
                try:
                    check_monitor(m.id)
                except Exception as exc:  # noqa: BLE001 - scheduler must continue after one monitor fails
                    print(f"[{m.id}] {m.name}: {exc}")

        time.sleep(poll)