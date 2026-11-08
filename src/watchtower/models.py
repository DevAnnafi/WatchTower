from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Monitor:
    id: int
    name: str
    url: str
    selector: str | None
    interval_minutes: int
    enabled: bool
    last_checked: str | None
    last_changed: str | None
    last_hash: str | None
    status: str = "SUCCESS"
    last_attempted: str | None = None
    last_successful: str | None = None


@dataclass(slots=True)
class CheckResult:
    changed: bool
    monitor: Monitor
    old_text: str
    new_text: str
    diff: str
    checked_at: datetime
