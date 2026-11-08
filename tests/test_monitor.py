import importlib


def test_baseline_then_change(tmp_path, monkeypatch):
    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))
    from watchtower import config, db, monitor

    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(monitor)
    mid = db.add_monitor("X", "https://x.test")
    monkeypatch.setattr(monitor, "fetch", lambda *args, **kwargs: "<p>one</p>")
    assert monitor.check_monitor(mid, False).changed is False
    monkeypatch.setattr(monitor, "fetch", lambda *args, **kwargs: "<p>two</p>")
    result = monitor.check_monitor(mid, False)
    assert result.changed is True
    assert "-one" in result.diff and "+two" in result.diff

def test_missing_selector_preserves_baseline(tmp_path, monkeypatch):
    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))

    import importlib

    from watchtower import config, db, monitor

    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(monitor)

    mid = db.add_monitor(
        "Product Price",
        "https://example.com",
        selector=".price",
    )

    monkeypatch.setattr(
        monitor,
        "fetch",
        lambda *args, **kwargs: '<span class="price">$99</span>',
    )

    monitor.check_monitor(mid, False)

    baseline = db.latest_version(mid)
    assert baseline["content"] == "$99"

    monkeypatch.setattr(
        monitor,
        "fetch",
        lambda *args, **kwargs: '<span class="item-price">$99</span>',
    )

    result = monitor.check_monitor(mid, False)

    assert result.changed is False
    assert result.monitor.status == "TARGET_NOT_FOUND"

    latest = db.latest_version(mid)
    assert latest["content"] == "$99"

    assert len(db.history(mid)) == 0

def test_selector_recovery_preserves_comparison(tmp_path, monkeypatch):
    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))

    from watchtower import config, db, monitor
    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(monitor)

    mid = db.add_monitor(
        "Product Price",
        "https://example.com",
        selector=".price",
    )

    html = {"content": '<span class="price">$99</span>'}

    monkeypatch.setattr(
        monitor,
        "fetch",
        lambda *args, **kwargs: html["content"],
    )

    first = monitor.check_monitor(mid, False)
    assert first.changed is False
    assert first.monitor.status == "SUCCESS"

    html["content"] = '<span class="item-price">$99</span>'

    failed = monitor.check_monitor(mid, False)
    assert failed.changed is False
    assert failed.monitor.status == "TARGET_NOT_FOUND"

    html["content"] = '<span class="price">$99</span>'

    recovered = monitor.check_monitor(mid, False)
    assert recovered.changed is False
    assert recovered.monitor.status == "SUCCESS"
    assert len(db.history(mid)) == 0

    html["content"] = '<span class="price">$79</span>'

    changed = monitor.check_monitor(mid, False)
    assert changed.changed is True
    assert changed.monitor.status == "SUCCESS"
    assert changed.old_text == "$99"
    assert changed.new_text == "$79"
    assert len(db.history(mid)) == 1

def test_empty_element_is_valid_content(tmp_path, monkeypatch):
    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))

    from watchtower import config, db, monitor
    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(monitor)

    mid = db.add_monitor(
        "Product Price",
        "https://example.com",
        selector=".price",
    )

    html = {"content": '<span class="price">$99</span>'}

    monkeypatch.setattr(
        monitor,
        "fetch",
        lambda *args, **kwargs: html["content"],
    )

    monitor.check_monitor(mid, False)

    html["content"] = '<span class="price"></span>'

    result = monitor.check_monitor(mid, False)

    assert result.monitor.status == "SUCCESS"
    assert result.changed is True
    assert result.old_text == "$99"
    assert result.new_text == ""

    latest = db.latest_version(mid)
    assert latest["content"] == ""
    assert len(db.history(mid)) == 1


def test_fetch_error_records_failure_and_preserves_baseline(
    tmp_path, monkeypatch
):
    import importlib

    from watchtower import config, db, monitor
    from watchtower.fetcher import FetchError

    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))

    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(monitor)

    mid = db.add_monitor(
        "Example",
        "https://example.com",
        ".price",
        60,
    )

    successful_at = "2026-11-01T12:00:00+00:00"

    db.save_version(mid, "$99", "original-hash", successful_at)
    db.update_check(mid, successful_at, "original-hash")

    def failing_fetch(*args, **kwargs):
        raise FetchError("Connection timed out")

    monkeypatch.setattr(monitor, "fetch", failing_fetch)

    import pytest

    with pytest.raises(FetchError, match="Connection timed out"):
        monitor.check_monitor(mid, send_notifications=False)

    updated = db.get_monitor(mid)
    latest = db.latest_version(mid)

    assert updated.status == "FETCH_ERROR"
    assert updated.last_attempted is not None
    assert updated.last_attempted != successful_at
    assert updated.last_successful == successful_at
    assert updated.last_hash == "original-hash"

    assert latest["content"] == "$99"
    assert latest["content_hash"] == "original-hash"
    assert db.history(mid) == []


def test_fetch_error_recovery_detects_change(tmp_path, monkeypatch):
    import importlib

    import pytest

    from watchtower import config, db, monitor
    from watchtower.fetcher import FetchError

    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))

    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(monitor)

    mid = db.add_monitor(
        "Price Monitor",
        "https://example.com",
        ".price",
        60,
    )

    monkeypatch.setattr(
        monitor,
        "fetch",
        lambda *args, **kwargs: '<span class="price">$99</span>',
    )

    first = monitor.check_monitor(mid, send_notifications=False)

    assert first.changed is False
    assert db.latest_version(mid)["content"] == "$99"

    # The website becomes unreachable.
    def failing_fetch(*args, **kwargs):
        raise FetchError("Connection timed out")

    monkeypatch.setattr(monitor, "fetch", failing_fetch)

    with pytest.raises(FetchError):
        monitor.check_monitor(mid, send_notifications=False)

    failed = db.get_monitor(mid)

    assert failed.status == "FETCH_ERROR"
    assert db.latest_version(mid)["content"] == "$99"
    assert db.history(mid) == []

    monkeypatch.setattr(
        monitor,
        "fetch",
        lambda *args, **kwargs: '<span class="price">$79</span>',
    )

    recovered = monitor.check_monitor(
        mid,
        send_notifications=False,
    )

    assert recovered.monitor.status == "SUCCESS"
    assert recovered.changed is True
    assert recovered.old_text == "$99"
    assert recovered.new_text == "$79"

    assert db.latest_version(mid)["content"] == "$79"
    assert len(db.history(mid)) == 1

    unchanged = monitor.check_monitor(
        mid,
        send_notifications=False,
    )

    assert unchanged.changed is False
    assert len(db.history(mid)) == 1
