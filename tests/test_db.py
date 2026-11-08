import importlib
import sqlite3


def test_monitor_crud(tmp_path, monkeypatch):
    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))
    from watchtower import config, db

    importlib.reload(config)
    importlib.reload(db)
    mid = db.add_monitor("Example", "https://example.com", ".x", 5)
    assert db.get_monitor(mid).name == "Example"
    assert len(db.list_monitors()) == 1
    assert db.remove_monitor(mid)

def test_existing_database_migration(tmp_path, monkeypatch):
    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))

    from watchtower import config, db
    importlib.reload(config)
    importlib.reload(db)

    # Simulate the original v1.0.1 monitors table.
    with sqlite3.connect(db.DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE monitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                selector TEXT,
                interval_minutes INTEGER NOT NULL DEFAULT 60,
                enabled INTEGER NOT NULL DEFAULT 1,
                last_checked TEXT,
                last_changed TEXT,
                last_hash TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            INSERT INTO monitors (
                name, url, selector, last_checked,
                last_hash, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Existing Monitor",
                "https://example.com",
                ".price",
                "2026-11-01T12:00:00+00:00",
                "original-hash",
                "2026-10-01T12:00:00+00:00",
            ),
        )

    monitor = db.get_monitor(1)

    assert monitor is not None
    assert monitor.name == "Existing Monitor"
    assert monitor.selector == ".price"
    assert monitor.last_hash == "original-hash"

    assert monitor.status == "SUCCESS"
    assert monitor.last_successful == "2026-11-01T12:00:00+00:00"

    monitor_again = db.get_monitor(1)
    assert monitor_again.status == "SUCCESS"
