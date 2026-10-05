from __future__ import annotations

import time

import httpx


class FetchError(RuntimeError): pass

def fetch(url: str, timeout: float = 15, user_agent: str = "Watchtower/1.0", retries: int = 2) -> str:
    headers = {"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"}
    last = None
    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
                r = client.get(url)
                r.raise_for_status()
                ctype = r.headers.get("content-type", "")
                if "html" not in ctype and "text" not in ctype and ctype:
                    raise FetchError(f"Unsupported content type: {ctype}")
                return r.text
        except (httpx.HTTPError, FetchError) as exc:
            last = exc
            if attempt < retries:
                time.sleep(0.5 * (2 ** attempt))
    raise FetchError(str(last))
