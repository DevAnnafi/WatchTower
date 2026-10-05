import importlib


def test_monitor_crud(tmp_path, monkeypatch):
    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))
    from watchtower import config, db

    importlib.reload(config)
    importlib.reload(db)
    mid = db.add_monitor("Example", "https://example.com", ".x", 5)
    assert db.get_monitor(mid).name == "Example"
    assert len(db.list_monitors()) == 1
    assert db.remove_monitor(mid)
