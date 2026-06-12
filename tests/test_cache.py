from pathlib import Path

from src.llm.cache import SQLiteLLMCache


def test_cache_returns_unexpired_value(tmp_path: Path) -> None:
    now = [100.0]
    cache = SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60, clock=lambda: now[0])

    cache.set("key", {"text": "cached"})
    now[0] = 159.0

    assert cache.get("key") == {"text": "cached"}


def test_cache_evicts_expired_value(tmp_path: Path) -> None:
    now = [100.0]
    cache = SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60, clock=lambda: now[0])

    cache.set("key", {"text": "cached"})
    now[0] = 161.0

    assert cache.get("key") is None
