from __future__ import annotations

import re

from bs4 import BeautifulSoup

NOISY = {"script", "style", "noscript", "svg", "canvas", "template"}


def extract_text(html: str, selector: str | None = None) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(NOISY):
        tag.decompose()

    if selector:
        selected = soup.select(selector)
        if not selected:
            raise ValueError(f"CSS selector matched no elements: {selector}")
        text = "\n".join(element.get_text(" ", strip=True) for element in selected)
    else:
        text = soup.get_text("\n", strip=True)

    lines = []
    for line in text.splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        if clean:
            lines.append(clean)
    return "\n".join(lines)
