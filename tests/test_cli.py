from datetime import datetime, timezone

from typer.testing import CliRunner

from watchtower import cli
from watchtower.models import CheckResult, Monitor

runner = CliRunner()

def make_monitor(status="SUCCESS"):
    return Monitor(
        id=1,
        name="Example Monitor",
        url="https://example.com",
        selector=".price",
        interval_minutes=60,
        enabled=True,
        last_checked=None,
        last_changed=None,
        last_hash=None,
        status=status,
        last_attempted="2026-11-08T12:00:00+00:00",
        last_successful="2026-11-08T11:00:00+00:00",
    )


def test_missing_selector_returns_exit_code_one(monkeypatch):
    monitor = make_monitor(status="TARGET_NOT_FOUND")

    monkeypatch.setattr(cli.db, "get_monitor", lambda mid: monitor)

    def fake_check(mid):
        return CheckResult(
            changed=False,
            monitor=monitor,
            old_text="$99",
            new_text="$99",
            diff="",
            checked_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(cli, "check_monitor", fake_check)

    result = runner.invoke(cli.app, ["check", "1"])

    assert result.exit_code == 1
    assert "TARGET_NOT_FOUND" in result.output
    assert "Previous snapshot preserved" in result.output
    assert "2026-11-08T11:00:00+00:00" in result.output


def test_successful_check_returns_exit_code_zero(monkeypatch):
    monitor = make_monitor()

    monkeypatch.setattr(cli.db, "get_monitor", lambda mid: monitor)

    def fake_check(mid):
        return CheckResult(
            changed=False,
            monitor=monitor,
            old_text="$99",
            new_text="$99",
            diff="",
            checked_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(cli, "check_monitor", fake_check)

    result = runner.invoke(cli.app, ["check", "1"])

    assert result.exit_code == 0
    assert "unchanged/baselined" in result.output


def test_unexpected_error_returns_exit_code_one(monkeypatch):
    monitor = make_monitor()

    monkeypatch.setattr(cli.db, "get_monitor", lambda mid: monitor)

    def fake_check(mid):
        raise ConnectionError("Connection timed out")

    monkeypatch.setattr(cli, "check_monitor", fake_check)

    result = runner.invoke(cli.app, ["check", "1"])

    assert result.exit_code == 1
    assert "Connection timed out" in result.output
