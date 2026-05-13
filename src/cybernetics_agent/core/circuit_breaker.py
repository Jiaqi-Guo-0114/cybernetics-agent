"""
熔断器模块。

实现电路熔断器模式，用于隔离失败服务。
"""

from __future__ import annotations

import threading
import time
from enum import Enum
from typing import Any


class CircuitState(Enum):
    """熔断器状态。"""
    CLOSED = "closed"      # 正常状态，允许请求通过
    OPEN = "open"          # 熔断状态，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复


class CircuitBreaker:
    """
    熔断器。

    当失败次数超过阈值时，进入开放状态拒绝请求，
    经过恢复超时后转入半开状态尝试恢复。
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._lock = threading.Lock()

    def can_execute(self) -> bool:
        """检查是否允许执行请求。"""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    return True
                return False

            if self._state == CircuitState.HALF_OPEN:
                return self._success_count < self._half_open_max_calls

            return False

    def record_success(self) -> None:
        """记录一次成功。"""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count = max(0, self._failure_count - 1)

    def record_failure(self) -> None:
        """记录一次失败。"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN or (
                self._state == CircuitState.CLOSED and self._failure_count >= self._failure_threshold
            ):
                self._state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置。"""
        if self._last_failure_time is None:
            return True
        return (time.time() - self._last_failure_time) >= self._recovery_timeout

    def get_status(self) -> dict[str, Any]:
        """获取熔断器状态。"""
        return {
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self._failure_threshold,
        }
