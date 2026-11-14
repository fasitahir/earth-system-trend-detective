"""In-process TTL cache for expensive, deterministic API reads."""

from __future__ import annotations

import hashlib
import json
import time
from threading import Lock
from typing import Any, Optional, Tuple


class TTLCache:
    """Small thread-safe TTL cache. Keys are hashed JSON payloads."""

    def __init__(self, ttl_seconds: int = 300, max_items: int = 256):
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._store: dict[str, Tuple[float, Any]] = {}
        self._lock = Lock()

    def make_key(self, **parts: Any) -> str:
        payload = json.dumps(parts, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        now = time.monotonic()
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at < now:
                self._store.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        expires_at = time.monotonic() + self.ttl_seconds
        with self._lock:
            if len(self._store) >= self.max_items:
                oldest_key = min(self._store, key=lambda k: self._store[k][0])
                self._store.pop(oldest_key, None)
            self._store[key] = (expires_at, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


response_cache = TTLCache(ttl_seconds=300, max_items=256)
