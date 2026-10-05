from dataclasses import dataclass

@dataclass(slots=True)
class Notification:
    title: str
    body: str
    url: str
