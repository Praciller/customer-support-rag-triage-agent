import json
import sqlite3
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any


class SQLiteLLMCache:
    def __init__(
        self,
        path: Path,
        ttl_seconds: int,
        clock: Callable[[], float] = time.time,
        enabled: bool = True,
    ) -> None:
        self.path = Path(path)
        self.ttl_seconds = ttl_seconds
        self.clock = clock
        self.enabled = enabled
        self._lock = threading.Lock()
        if enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_cache (
                    cache_key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )

    def get(self, key: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT value, created_at FROM llm_cache WHERE cache_key = ?",
                (key,),
            ).fetchone()
            if row is None:
                return None
            value, created_at = row
            if self.clock() - created_at <= self.ttl_seconds:
                return json.loads(value)
            connection.execute("DELETE FROM llm_cache WHERE cache_key = ?", (key,))
            return None

    def set(self, key: str, value: dict[str, Any]) -> None:
        if not self.enabled:
            return
        payload = json.dumps(value, sort_keys=True)
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO llm_cache(cache_key, value, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    value = excluded.value,
                    created_at = excluded.created_at
                """,
                (key, payload, self.clock()),
            )
