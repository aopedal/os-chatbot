import logging
import os
import time
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PATH = Path(os.getenv("SETTINGS_PATH", "./settings.toml"))
_TTL = 10  # seconds between automatic re-reads

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
        _read()
    return _cache


def get(key: str, default: Any = None) -> Any:
    return load().get(key, default)


def mtime() -> str | None:
    if _mtime is None:
        return None
    return datetime.fromtimestamp(_mtime).isoformat(timespec="seconds")
