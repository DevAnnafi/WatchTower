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


def test_migration_preserves_existing_history(tmp_path, monkeypatch):
    monkeypatch.setenv("WATCHTOWER_HOME", str(tmp_path))

    from watchtower import config, db

    importlib.reload(config)
    importlib.reload(db)

    with sqlite3.connect(db.DB_PATH) as conn:
        conn.executescript(
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
            );

            CREATE TABLE versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                FOREIGN KEY(monitor_id)
                    REFERENCES monitors(id) ON DELETE CASCADE
            );

            CREATE TABLE changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                old_hash TEXT,
                new_hash TEXT NOT NULL,
                diff TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                FOREIGN KEY(monitor_id)
                    REFERENCES monitors(id) ON DELETE CASCADE
            );
            """
        )

        conn.execute(
            """
            INSERT INTO monitors (
                id, name, url, selector,
                last_checked, last_changed,
                last_hash, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                "Price Monitor",
                "https://example.com",
                ".price",
                "2026-11-01T12:00:00+00:00",
                "2026-11-01T12:00:00+00:00",
                "hash-new",
                "2026-10-01T12:00:00+00:00",
            ),
        )

        conn.executemany(
            """
            INSERT INTO versions (
                monitor_id, content,
                content_hash, captured_at
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    1, "$99", "hash-old",
                    "2026-10-01T12:00:00+00:00",
                ),
                (
                    1, "$79", "hash-new",
                    "2026-11-01T12:00:00+00:00",
                ),
            ],
        )

        conn.execute(
            """
            INSERT INTO changes (
                monitor_id, old_hash,
                new_hash, diff, detected_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                1,
                "hash-old",
                "hash-new",
                "-$99\n+$79",
                "2026-11-01T12:00:00+00:00",
            ),
        )

    monitor = db.get_monitor(1)

    assert monitor is not None
    assert monitor.status == "SUCCESS"
    assert monitor.last_hash == "hash-new"
    assert monitor.last_successful == "2026-11-01T12:00:00+00:00"

    latest = db.latest_version(1)
    assert latest["content"] == "$79"
    assert latest["content_hash"] == "hash-new"

    with db.connect() as conn:
        versions = conn.execute(
            """
            SELECT content, content_hash
            FROM versions
            WHERE monitor_id = ?
            ORDER BY id
            """,
            (1,),
        ).fetchall()

    assert [(v["content"], v["content_hash"]) for v in versions] == [
        ("$99", "hash-old"),
        ("$79", "hash-new"),
    ]

    changes = db.history(1)
    assert len(changes) == 1
    assert changes[0]["old_hash"] == "hash-old"
    assert changes[0]["new_hash"] == "hash-new"
    assert changes[0]["diff"] == "-$99\n+$79"

    db.get_monitor(1)

    assert db.latest_version(1)["content"] == "$79"
    assert len(db.history(1)) == 1

