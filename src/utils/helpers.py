"""
Speed-ZeroBaran — Helper utilities
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional


def utc_now_iso() -> str:
    """Current UTC timestamp in ISO-8601."""
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    """Make a string safe for filenames / IDs."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def short_hash(text: str, length: int = 8) -> str:
    """Short stable hash (used for run IDs)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def timed(fn: Callable) -> Callable:
    """Decorator: logs how long a function took."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            from .logger import log
            elapsed = time.perf_counter() - start
            log.debug(f"{fn.__name__} finished in {elapsed:.2f}s")
    return wrapper


def safe_json(obj: Any) -> str:
    """JSON-encode with fallback for non-serializable objects."""
    def default(o):
        if hasattr(o, "to_dict"):
            return o.to_dict()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    return json.dumps(obj, default=default, ensure_ascii=False, indent=2)


def truncate(text: str, limit: int = 1500) -> str:
    """Trim long texts before sending them to LLMs."""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…[truncated]"


def format_bytes(num_bytes: Optional[int | float]) -> str:
    """Human-readable byte size."""
    if not num_bytes:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"


__all__ = [
    "utc_now_iso",
    "slugify",
    "short_hash",
    "timed",
    "safe_json",
    "truncate",
    "format_bytes",
]
