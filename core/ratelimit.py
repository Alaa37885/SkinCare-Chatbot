import time
import random
import asyncio
import threading

from collections import deque
from langchain_core.runnables import RunnableConfig


# =========================
# RATE LIMITER 
# =========================
class RPMGroqRateLimiter:

    def __init__(self, rpm: int = 30, window_s: float = 60.0):

        self.rpm = rpm
        self.window_s = window_s
        self._req_timestamps = deque()
        self._lock = threading.Lock()

    def _purge_expired(self, now: float):
        cutoff = now - self.window_s

        while self._req_timestamps and self._req_timestamps[0] < cutoff:
            self._req_timestamps.popleft()

    def acquire(self, timeout: float = 90.0):

        deadline = time.monotonic() + timeout

        while True:

            with self._lock:
                now = time.monotonic()
                self._purge_expired(now)

                if len(self._req_timestamps) < self.rpm:
                    self._req_timestamps.append(now)
                    return True

            if time.monotonic() > deadline:
                raise TimeoutError("Rate limit acquire timed out")

            time.sleep(0.2)

