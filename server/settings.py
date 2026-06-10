import logging
import os
import time
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PATH = Path(os.getenv("SETTINGS_PATH", "./settings.toml"))
_TTL = 1  # seconds between mtime checks

_cache: dict[str, Any] = {}
_cache_time: float = 0.0
_mtime: float | None = None


def _read() -> None:
    global _cache, _cache_time, _mtime
    try:
        stat = _PATH.stat()
        _mtime = stat.st_mtime
        with _PATH.open("rb") as f:
            _cache = tomllib.load(f)
    except FileNotFoundError:
        logger.error(
            "settings.toml not found at %s — set SETTINGS_PATH or create the file. "
            "Server will not function correctly.",
            _PATH.resolve(),
        )
        _cache = {}
        _mtime = None
    _cache_time = time.monotonic()


def load() -> dict[str, Any]:
    if (time.monotonic() - _cache_time) > _TTL:
        _check()
    return _cache


def _check() -> None:
    global _cache_time
    try:
        new_mtime = _PATH.stat().st_mtime
    except FileNotFoundError:
        _cache_time = time.monotonic()
        return
    if _mtime is None or new_mtime != _mtime:
        _read()
    else:
        _cache_time = time.monotonic()


def get(key: str, default: Any = None) -> Any:
    return load().get(key, default)


def path() -> Path:
    return _PATH


def save(content: str) -> None:
    """Validate content as TOML, write to file, and reset the read cache."""
    global _cache, _cache_time
    tomllib.loads(content)  # raises TOMLDecodeError if invalid
    _PATH.write_text(content, encoding="utf-8")
    _cache = {}
    _cache_time = 0.0


def mtime() -> str | None:
    if _mtime is None:
        return None
    return datetime.fromtimestamp(_mtime).isoformat(timespec="seconds")
