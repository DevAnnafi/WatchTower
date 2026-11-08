from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from . import db
from .config import CONFIG_PATH, DB_PATH, load_config
from .monitor import check_monitor
from .notifications import Notification, notify
from .scheduler import run_forever

app = typer.Typer(
    help="Watchtower - monitor websites and get notified when they change.",
    no_args_is_help=True,
)
console = Console()


@app.command("init")
def init():
    load_config()
    with db.connect():
        pass
    console.print(
        f"Initialized Watchtower\n"
        f"Config: {CONFIG_PATH}\n"
        f"Database: {DB_PATH}"
    )


@app.command("add")
def add(
    url: str,
    name: str = typer.Option(None, "--name", "-n"),
    selector: str = typer.Option(None, "--selector", "-s"),
    interval: int = typer.Option(60, "--interval", "-i", min=1),
):
    mid = db.add_monitor(name or url, url, selector, interval)
    console.print(f"Added monitor [bold]#{mid}[/bold]: {name or url}")


@app.command("list")
def ls():
    table = Table(
        "ID",
        "Name",
        "URL",
        "Selector",
        "Every",
        "Enabled",
        "Status",
        "Last successful",
        "Last changed",
    )

    for m in db.list_monitors():
        if m.status == "TARGET_NOT_FOUND":
            status = "[yellow]TARGET_NOT_FOUND[/yellow]"
        elif m.last_successful is None:
            status = "[dim]NOT_CHECKED[/dim]"
        else:
            status = "[green]SUCCESS[/green]"

        table.add_row(
            str(m.id),
            m.name,
            m.url,
            m.selector or "-",
            f"{m.interval_minutes}m",
            "yes" if m.enabled else "no",
            status,
            m.last_successful or "-",
            m.last_changed or "-",
        )

    console.print(table)


@app.command("remove")
def remove(mid: int):
    if not db.remove_monitor(mid):
        raise typer.BadParameter(f"Monitor {mid} not found")
    console.print(f"Removed monitor #{mid}")


@app.command("enable")
def enable(mid: int):
    db.set_enabled(mid, True)
    console.print(f"Enabled #{mid}")


@app.command("disable")
def disable(mid: int):
    db.set_enabled(mid, False)
    console.print(f"Disabled #{mid}")


@app.command("check")
def check(mid: int = typer.Argument(None)):
    monitors = [db.get_monitor(mid)] if mid else db.list_monitors()
    monitors = [m for m in monitors if m]

    if not monitors:
        console.print("No monitors found.")
        raise typer.Exit()

    had_failure = False

    for m in monitors:
        try:
            result = check_monitor(m.id)

            if result.monitor.status == "TARGET_NOT_FOUND":
                had_failure = True
                console.print(
                    f"[yellow]#{m.id} {m.name}: TARGET_NOT_FOUND[/yellow]"
                )
                console.print(
                    f"  Selector: {result.monitor.selector}"
                )
                console.print(
                    "  Last successful check: "
                    f"{result.monitor.last_successful or 'Never'}"
                )
                console.print(
                    "  Previous snapshot preserved."
                )

            elif result.changed:
                console.print(
                    f"#{m.id} {m.name}: [yellow]CHANGED[/yellow]"
                )

            else:
                console.print(
                    f"#{m.id} {m.name}: "
                    "[green]unchanged/baselined[/green]"
                )

        except Exception as exc:  # noqa: BLE001
            had_failure = True
            console.print(
                f"[red]#{m.id} {m.name}: {exc}[/red]"
            )

    if had_failure:
        raise typer.Exit(code=1)


@app.command("history")
def history(mid: int, limit: int = 20):
    rows = db.history(mid, limit)
    table = Table("Change ID", "Detected")

    for row in rows:
        table.add_row(
            str(row["id"]),
            row["detected_at"],
        )

    console.print(table)


@app.command("diff")
def diff(change_id: int):
    row = db.get_change(change_id)

    if not row:
        raise typer.BadParameter("Change not found")

    console.print(row["diff"])


@app.command("run")
def run():
    console.print("Watchtower scheduler running. Press Ctrl+C to stop.")

    try:
        run_forever()
    except KeyboardInterrupt:
        console.print("Stopped.")


@app.command("test-notification")
def test_notification():
    errors = notify(
        Notification(
            "Watchtower test",
            "Notifications are configured correctly.",
            "https://example.com",
        ),
        load_config(),
    )

    for error in errors:
        console.print(f"[red]{error}[/red]")


if __name__ == "__main__":
    app()
