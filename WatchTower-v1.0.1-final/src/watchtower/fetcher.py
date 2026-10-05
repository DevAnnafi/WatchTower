from __future__ import annotations

import time

import httpx


class FetchError(RuntimeError):
    pass


def fetch(
    url: str,
    timeout: float = 15,
    user_agent: str = "Watchtower/1.0",
    retries: int = 2,
) -> str:
    headers = {"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"}
    last = None

    for attempt in range(retries + 1):
        try:
            with httpx.Client(
                timeout=timeout,
                follow_redirects=True,
                headers=headers,
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if "html" not in content_type and "text" not in content_type and content_type:
                    raise FetchError(f"Unsupported content type: {content_type}")
                return response.text
        except (httpx.HTTPError, FetchError) as exc:
            last = exc
            if attempt < retries:
                time.sleep(0.5 * (2**attempt))

    raise FetchError(str(last))
