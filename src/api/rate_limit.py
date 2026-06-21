import math
import threading
import time
from collections import OrderedDict, deque
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after_seconds: int


class InMemoryRateLimiter:
    def __init__(
        self,
        clock: Callable[[], float] = time.monotonic,
        max_keys: int = 10_000,
    ) -> None:
        self.clock = clock
        self.max_keys = max_keys
        self._requests: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> RateLimitDecision:
        now = self.clock()
        cutoff = now - window_seconds
        with self._lock:
            timestamps = self._requests.get(key)
            if timestamps is None:
                self._evict_key_if_full()
                timestamps = deque()
                self._requests[key] = timestamps
            else:
                self._requests.move_to_end(key)

            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= limit:
                retry_after = max(1, math.ceil(timestamps[0] + window_seconds - now))
                return RateLimitDecision(False, 0, retry_after)

            timestamps.append(now)
            return RateLimitDecision(True, max(0, limit - len(timestamps)), 0)

    def _evict_key_if_full(self) -> None:
        if len(self._requests) >= self.max_keys:
            self._requests.popitem(last=False)
