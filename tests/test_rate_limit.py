from src.api.rate_limit import InMemoryRateLimiter


def test_rate_limiter_resets_after_window() -> None:
    now = [100.0]
    limiter = InMemoryRateLimiter(clock=lambda: now[0], max_keys=10)

    first = limiter.check("triage:127.0.0.1", limit=2, window_seconds=60)
    second = limiter.check("triage:127.0.0.1", limit=2, window_seconds=60)
    blocked = limiter.check("triage:127.0.0.1", limit=2, window_seconds=60)
    now[0] = 161.0
    reset = limiter.check("triage:127.0.0.1", limit=2, window_seconds=60)

    assert first.allowed is True
    assert second.remaining == 0
    assert blocked.allowed is False
    assert blocked.retry_after_seconds == 60
    assert reset.allowed is True
