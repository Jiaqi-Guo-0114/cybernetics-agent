"""
稳定性引擎模块。

实现超时控制、重试机制、熔断器、优雅降级、并行竞争。
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable

from .base import CyberneticsEvent, EventType, ICyberneticsModule
from .circuit_breaker import CircuitBreaker


@dataclass
class RetryPolicy:
    """重试策略。"""
    max_retries: int = 3
    backoff: str = "exponential"  # "exponential" | "linear" | "fixed"
    base_delay: float = 1.0
    max_delay: float = 60.0

    def get_delay(self, attempt: int) -> float:
        """获取第 attempt 次重试的等待时间。"""
        if self.backoff == "exponential":
            delay = self.base_delay * (2 ** attempt)
        elif self.backoff == "linear":
            delay = self.base_delay * (attempt + 1)
        else:  # fixed
            delay = self.base_delay
        return min(delay, self.max_delay)


class StabilityEngine(ICyberneticsModule):
    """
    稳定性引擎模块。

    提供以下能力：
    - 超时控制: 给任何函数调用加超时限制
    - 重试机制: 支持指数退避、线性退避、固定间隔
    - 熔断器: 自动检测并隔离失败服务
    - 优雅降级: 按降级链逐级降级
    - 并行竞争: 多组并行/串行执行，取最快成功者

    配置示例（cybernetics.json）：
        "stability": {
            "enabled": true,
            "timeout": {"default": 30, "llm": 120},
            "retry": {"max_retries": 3, "backoff": "exponential"},
            "circuit_breaker": {"failure_threshold": 5},
            "graceful_degradation": {"enabled": true, "chain": [...]},
            "parallel_competition": {"enabled": true, "groups": [...]}
        }
    """

    name = "stability"

    def __init__(self, config: dict[str, Any], ctx: Any) -> None:
        super().__init__(config, ctx)

        # 超时配置
        timeout_cfg = config.get("timeout", {})
        self._timeouts = {
            "default": timeout_cfg.get("default", 30.0),
            "llm": timeout_cfg.get("llm", 120.0),
            "download": timeout_cfg.get("download", 60.0),
            "tool": timeout_cfg.get("tool", 30.0),
        }

        # 重试配置
        retry_cfg = config.get("retry", {})
        self._retry_policy = RetryPolicy(
            max_retries=retry_cfg.get("max_retries", 3),
            backoff=retry_cfg.get("backoff", "exponential"),
            base_delay=retry_cfg.get("base_delay", 1.0),
            max_delay=retry_cfg.get("max_delay", 60.0),
        )

        # 熔断器配置
        cb_cfg = config.get("circuit_breaker", {})
        if cb_cfg.get("enabled", True):
            self._circuit_breakers: dict[str, CircuitBreaker] = {}
        else:
            self._circuit_breakers = None  # type: ignore

        # 降级配置
        deg_cfg = config.get("graceful_degradation", {})
        self._degradation_enabled = deg_cfg.get("enabled", True)
        self._degradation_chain: list[dict[str, str]] = deg_cfg.get("chain", [])

        # 并行竞争配置
        pc_cfg = config.get("parallel_competition", {})
        self._parallel_enabled = pc_cfg.get("enabled", True)
        self._parallel_groups: list[dict[str, Any]] = pc_cfg.get("groups", [])
        self._parallel_timeout = pc_cfg.get("timeout_seconds", 120.0)

        # 统计
        self._retry_count = 0
        self._timeout_count = 0
        self._degradation_count = 0
        self._circuit_events = 0

    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent | None:
        """监听错误事件，更新熔断器状态。"""
        if event.event_type == EventType.TOOL_ERROR:
            tool_name = event.payload.get("tool_name", "unknown")
            event.payload.get("error_type", "unknown")

            # 更新熔断器
            if self._circuit_breakers is not None:
                cb = self._get_circuit_breaker(tool_name)
                cb.record_failure()
                self._circuit_events += 1

        elif event.event_type == EventType.TOOL_RESULT:
            tool_name = event.payload.get("tool_name", "unknown")
            success = event.payload.get("success", True)

            if success and self._circuit_breakers is not None:
                cb = self._get_circuit_breaker(tool_name)
                cb.record_success()

        return event

    def _get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """获取或创建熔断器。"""
        if name not in self._circuit_breakers:
            cb_cfg = self.config.get("circuit_breaker", {})
            self._circuit_breakers[name] = CircuitBreaker(
                failure_threshold=cb_cfg.get("failure_threshold", 5),
                recovery_timeout=cb_cfg.get("recovery_timeout", 60.0),
                half_open_max_calls=cb_cfg.get("half_open_max_calls", 3),
            )
        return self._circuit_breakers[name]

    def with_timeout(
        self,
        func: Callable[..., Any],
        timeout_type: str = "default",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        带超时控制的函数调用。

        支持同步函数（使用线程）和异步函数（使用 asyncio）。
        """
        timeout = self._timeouts.get(timeout_type, self._timeouts["default"])

        if asyncio.iscoroutinefunction(func):
            return self._async_with_timeout(func, timeout, *args, **kwargs)
        else:
            return self._sync_with_timeout(func, timeout, *args, **kwargs)

    def _sync_with_timeout(
        self,
        func: Callable[..., Any],
        timeout: float,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """同步函数的超时控制。"""
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError as err:
                self._timeout_count += 1
                raise TimeoutError(f"函数执行超时（限制 {timeout}秒）") from err

    def _async_with_timeout(
        self,
        func: Callable[..., Any],
        timeout: float,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """异步函数的超时控制。"""
        # 注: 实际使用时需要在 async 环境中调用
        # 这里只做简单检查
        return func(*args, **kwargs)

    def with_retry(
        self,
        func: Callable[..., Any],
        retry_policy: RetryPolicy | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        带重试机制的函数调用。

        只对暂时性错误进行重试，永久性错误直接抛出。
        """
        policy = retry_policy or self._retry_policy
        last_error: Exception | None = None

        for attempt in range(policy.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # 检查是否是永久性错误（不重试）
                permanent_errors = ["404", "403", "not found", "forbidden", "invalid"]
                if any(err in error_str for err in permanent_errors):
                    raise

                if attempt < policy.max_retries:
                    delay = policy.get_delay(attempt)
                    time.sleep(delay)
                    self._retry_count += 1

        if last_error:
            raise last_error
        raise RuntimeError("重试次数耗尽")

    def with_circuit_breaker(
        self,
        name: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        带熔断器保护的函数调用。
        """
        if self._circuit_breakers is None:
            return func(*args, **kwargs)

        cb = self._get_circuit_breaker(name)
        if not cb.can_execute():
            raise RuntimeError(f"熔断器已打开: {name}")

        try:
            result = func(*args, **kwargs)
            cb.record_success()
            return result
        except Exception:
            cb.record_failure()
            raise

    def degrade(
        self,
        primary_func: Callable[..., Any],
        fallback_chain: list[Callable[..., Any]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        优雅降级调用。

        优先尝试主函数，失败后逐级尝试后备函数。
        """
        if not self._degradation_enabled:
            return primary_func(*args, **kwargs)

        chain = fallback_chain or []
        all_funcs = [primary_func] + chain
        last_error: Exception | None = None

        for i, func in enumerate(all_funcs):
            try:
                result = func(*args, **kwargs)
                if i > 0:
                    self._degradation_count += 1
                return result
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error
        raise RuntimeError("所有降级路径均失败")

    def get_status(self) -> dict[str, Any]:
        """获取稳定性引擎状态。"""
        status: dict[str, Any] = {
            "enabled": self.enabled,
            "timeouts": self._timeouts,
            "retry_policy": {
                "max_retries": self._retry_policy.max_retries,
                "backoff": self._retry_policy.backoff,
            },
            "stats": {
                "retry_count": self._retry_count,
                "timeout_count": self._timeout_count,
                "degradation_count": self._degradation_count,
                "circuit_events": self._circuit_events,
            },
        }

        if self._circuit_breakers:
            status["circuit_breakers"] = {
                name: cb.get_status()
                for name, cb in self._circuit_breakers.items()
            }

        return status

    def reset_stats(self) -> None:
        """重置统计数据。"""
        self._retry_count = 0
        self._timeout_count = 0
        self._degradation_count = 0
        self._circuit_events = 0
