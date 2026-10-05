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
