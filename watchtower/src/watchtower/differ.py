from __future__ import annotations

import difflib
import hashlib


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def unified(old: str, new: str) -> str:
    return "\n".join(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile="previous", tofile="current", lineterm=""))

def summary(diff: str, limit: int = 12) -> str:
    useful = [
    	x
    	for x in diff.splitlines()
    	if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))
    ]
    if not useful:
        return "Content changed."
    clipped = useful[:limit]
    suffix = f"\n… {len(useful)-limit} more changed lines" if len(useful) > limit else ""
    return "\n".join(clipped) + suffix
