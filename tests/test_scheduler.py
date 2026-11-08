from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from watchtower.scheduler import _due


def test_failed_selector_respects_check_interval():
    now = datetime.now(timezone.utc)

    monitor = SimpleNamespace(
        last_checked=(now - timedelta(hours=2)).isoformat(),
        last_attempted=(now - timedelta(minutes=5)).isoformat(),
        interval_minutes=60,
    )

    assert _due(monitor, now) is False


def test_failed_selector_becomes_due_after_interval():
    now = datetime.now(timezone.utc)

    monitor = SimpleNamespace(
        last_checked=(now - timedelta(hours=2)).isoformat(),
        last_attempted=(now - timedelta(minutes=61)).isoformat(),
        interval_minutes=60,
    )

    assert _due(monitor, now) is True


def test_never_checked_monitor_is_due():
    now = datetime.now(timezone.utc)

    monitor = SimpleNamespace(
        last_checked=None,
        last_attempted=None,
        interval_minutes=60,
    )

    assert _due(monitor, now) is True