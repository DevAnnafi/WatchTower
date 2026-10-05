from rich.console import Console
from rich.panel import Panel

from .base import Notification


def send(n: Notification):
    Console().print(Panel(f"{n.body}\n\n{n.url}", title=n.title))
