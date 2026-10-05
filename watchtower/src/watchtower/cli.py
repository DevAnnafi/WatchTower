from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from . import db
from .config import CONFIG_PATH, DB_PATH, load_config
from .monitor import check_monitor
from .notifications import Notification, notify
from .scheduler import run_forever

app = typer.Typer(help="Watchtower — monitor websites and get notified when they change.", no_args_is_help=True)
console = Console()

@app.command("init")
def init():
    load_config(); db.connect().close()
    console.print(f"Initialized Watchtower\nConfig: {CONFIG_PATH}\nDatabase: {DB_PATH}")

@app.command("add")
def add(url: str, name: str = typer.Option(None, "--name", "-n"), selector: str = typer.Option(None, "--selector", "-s"), interval: int = typer.Option(60, "--interval", "-i", min=1)):
    mid = db.add_monitor(name or url, url, selector, interval)
    console.print(f"Added monitor [bold]#{mid}[/bold]: {name or url}")

@app.command("list")
def ls():
    table = Table("ID", "Name", "URL", "Selector", "Every", "Enabled", "Last changed")
    for m in db.list_monitors():
        table.add_row(str(m.id), m.name, m.url, m.selector or "—", f"{m.interval_minutes}m", "yes" if m.enabled else "no", m.last_changed or "—")
    console.print(table)

@app.command("remove")
def remove(mid: int):
    if not db.remove_monitor(mid): raise typer.BadParameter(f"Monitor {mid} not found")
    console.print(f"Removed monitor #{mid}")

@app.command("enable")
def enable(mid: int): db.set_enabled(mid, True); console.print(f"Enabled #{mid}")
@app.command("disable")
def disable(mid: int): db.set_enabled(mid, False); console.print(f"Disabled #{mid}")

@app.command("check")
def check(mid: int = typer.Argument(None)):
    monitors = [db.get_monitor(mid)] if mid else db.list_monitors()
    monitors = [m for m in monitors if m]
    if not monitors: console.print("No monitors found."); raise typer.Exit()
    for m in monitors:
        try:
            r = check_monitor(m.id)
            console.print(f"#{m.id} {m.name}: " + ("[yellow]CHANGED[/yellow]" if r.changed else "[green]unchanged/baselined[/green]"))
        except Exception as exc:  # noqa: BLE001 - CLI boundary must report individual monitor failures
    	    console.print(f"[red]#{m.id} {m.name}: {exc}[/red]")

@app.command("history")
def history(mid: int, limit: int = 20):
    rows = db.history(mid, limit)
    table = Table("Change ID", "Detected")
    for r in rows: table.add_row(str(r["id"]), r["detected_at"])
    console.print(table)

@app.command("diff")
def diff(change_id: int):
    row = db.get_change(change_id)
    if not row: raise typer.BadParameter("Change not found")
    console.print(row["diff"])

@app.command("run")
def run():
    console.print("Watchtower scheduler running. Press Ctrl+C to stop.")
    try: run_forever()
    except KeyboardInterrupt: console.print("Stopped.")

@app.command("test-notification")
def test_notification():
    errors = notify(Notification("Watchtower test", "Notifications are configured correctly.", "https://example.com"), load_config())
    for e in errors: console.print(f"[red]{e}[/red]")

if __name__ == "__main__": app()
