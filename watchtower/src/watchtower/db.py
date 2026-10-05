from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
from .config import DB_PATH, ensure_app_dir
from .models import Monitor

SCHEMA = """
CREATE TABLE IF NOT EXISTS monitors (
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
CREATE TABLE IF NOT EXISTS versions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 monitor_id INTEGER NOT NULL,
 content TEXT NOT NULL,
 content_hash TEXT NOT NULL,
 captured_at TEXT NOT NULL,
 FOREIGN KEY(monitor_id) REFERENCES monitors(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS changes (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 monitor_id INTEGER NOT NULL,
 old_hash TEXT,
 new_hash TEXT NOT NULL,
 diff TEXT NOT NULL,
 detected_at TEXT NOT NULL,
 FOREIGN KEY(monitor_id) REFERENCES monitors(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_versions_monitor ON versions(monitor_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_changes_monitor ON changes(monitor_id, id DESC);
"""

def connect():
    ensure_app_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    return conn

def _monitor(row) -> Monitor:
    return Monitor(row["id"], row["name"], row["url"], row["selector"], row["interval_minutes"], bool(row["enabled"]), row["last_checked"], row["last_changed"], row["last_hash"])

def add_monitor(name, url, selector=None, interval_minutes=60):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as c:
        cur = c.execute("INSERT INTO monitors(name,url,selector,interval_minutes,created_at) VALUES(?,?,?,?,?)", (name,url,selector,interval_minutes,now))
        return cur.lastrowid

def list_monitors():
    with connect() as c:
        return [_monitor(r) for r in c.execute("SELECT * FROM monitors ORDER BY id")]

def get_monitor(mid):
    with connect() as c:
        r = c.execute("SELECT * FROM monitors WHERE id=?", (mid,)).fetchone()
        return _monitor(r) if r else None

def remove_monitor(mid):
    with connect() as c:
        return c.execute("DELETE FROM monitors WHERE id=?", (mid,)).rowcount > 0

def set_enabled(mid, enabled):
    with connect() as c:
        c.execute("UPDATE monitors SET enabled=? WHERE id=?", (int(enabled),mid))

def latest_version(mid):
    with connect() as c:
        return c.execute("SELECT * FROM versions WHERE monitor_id=? ORDER BY id DESC LIMIT 1", (mid,)).fetchone()

def save_version(mid, content, content_hash, captured_at):
    with connect() as c:
        c.execute("INSERT INTO versions(monitor_id,content,content_hash,captured_at) VALUES(?,?,?,?)", (mid,content,content_hash,captured_at))

def save_change(mid, old_hash, new_hash, diff, detected_at):
    with connect() as c:
        c.execute("INSERT INTO changes(monitor_id,old_hash,new_hash,diff,detected_at) VALUES(?,?,?,?,?)", (mid,old_hash,new_hash,diff,detected_at))

def update_check(mid, checked_at, content_hash, changed=False):
    with connect() as c:
        if changed:
            c.execute("UPDATE monitors SET last_checked=?,last_changed=?,last_hash=? WHERE id=?", (checked_at,checked_at,content_hash,mid))
        else:
            c.execute("UPDATE monitors SET last_checked=?,last_hash=? WHERE id=?", (checked_at,content_hash,mid))

def history(mid, limit=20):
    with connect() as c:
        return c.execute("SELECT * FROM changes WHERE monitor_id=? ORDER BY id DESC LIMIT ?", (mid,limit)).fetchall()

def get_change(change_id):
    with connect() as c:
        return c.execute("SELECT * FROM changes WHERE id=?", (change_id,)).fetchone()
