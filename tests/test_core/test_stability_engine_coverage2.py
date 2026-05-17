"""补齐 stability_engine.py 未覆盖分支 — 熔断器禁用、异步超时、永久性错误、降级关闭、线性回退。"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.stability_engine import RetryPolicy, StabilityEngine


class TestRetryPolicyBranches:
    def test_linear_backoff(self):
        rp = RetryPolicy(max_retries=3, backoff="linear", base_delay=2.0)
        assert rp.get_delay(0) == 2.0
        assert rp.get_delay(1) == 4.0
        assert rp.get_delay(2) == 6.0

    def test_fixed_backoff(self):
        rp = RetryPolicy(max_retries=3, backoff="fixed", base_delay=5.0)
        assert rp.get_delay(0) == 5.0
        assert rp.get_delay(2) == 5.0

    def test_delay_max_cap(self):
        rp = RetryPolicy(max_retries=10, backoff="exponential", base_delay=10.0, max_delay=50.0)
        assert rp.get_delay(10) == 50.0


class TestStabilityEngineBranches:
    def test_circuit_breaker_disabled(self):
        ctx = MagicMock()
        se = StabilityEngine(
            config={"circuit_breaker": {"enabled": False}},
            ctx=ctx,
        )
        assert se._circuit_breakers is None
        # with_circuit_breaker should bypass
        result = se.with_circuit_breaker("test", lambda: 42)
        assert result == 42

    def test_async_with_timeout(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)

        async def async_func():
            return "async_result"

        coro = se._async_with_timeout(async_func, 1.0)
        assert asyncio.iscoroutine(coro)
        # 正确 await 并验证结果，避免 coroutine never awaited warning
        result = asyncio.run(coro)
        assert result == "async_result"

    def test_with_timeout_detects_async(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)

        async def actual_async():
            return "async_result"

        # 预创建 coroutine object，避免在 ThreadPoolExecutor 线程中创建未 awaited 的 coroutine
        coro = actual_async()

        def func_that_returns_coro():
            return coro

        result = se.with_timeout(func_that_returns_coro, timeout_type="default")
        assert asyncio.iscoroutine(result)
        result.close()  # 清理 coroutine 避免 warning

    def test_sync_timeout_raises(self):
        ctx = MagicMock()
        se = StabilityEngine(config={"timeout": {"default": 0.01}}, ctx=ctx)

        def slow_func():
            import time
            time.sleep(1)
            return "never"

        with pytest.raises(TimeoutError):
            se.with_timeout(slow_func, timeout_type="default")
        assert se._timeout_count == 1

    def test_retry_permanent_error(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)

        def fail_404():
            raise RuntimeError("HTTP 404 not found")

        with pytest.raises(RuntimeError, match="404"):
            se.with_retry(fail_404, RetryPolicy(max_retries=2))
        assert se._retry_count == 0

    def test_retry_exhausted(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)

        def fail_transient():
            raise RuntimeError("connection reset")

        with pytest.raises(RuntimeError, match="connection reset"):
            se.with_retry(fail_transient, RetryPolicy(max_retries=1, base_delay=0.01))
        assert se._retry_count == 1

    def test_retry_success_on_second(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)
        calls = []

        def fail_once():
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("boom")
            return "ok"

        result = se.with_retry(fail_once, RetryPolicy(max_retries=2, base_delay=0.01))
        assert result == "ok"
        assert se._retry_count == 1

    def test_circuit_breaker_open(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)
        cb = se._get_circuit_breaker("svc")
        cb._state = "open"
        with pytest.raises(RuntimeError, match="熔断器已打开"):
            se.with_circuit_breaker("svc", lambda: 1)

    def test_circuit_breaker_records_failure(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)

        def bad():
            raise ValueError("x")

        with pytest.raises(ValueError):
            se.with_circuit_breaker("svc", bad)
        cb = se._get_circuit_breaker("svc")
        assert cb._failure_count == 1

    def test_degradation_disabled(self):
        ctx = MagicMock()
        se = StabilityEngine(
            config={"graceful_degradation": {"enabled": False}},
            ctx=ctx,
        )
        result = se.degrade(lambda: "primary")
        assert result == "primary"

    def test_degradation_fallback_success(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)
        result = se.degrade(lambda: exec("raise ValueError"), [lambda: "fallback"])
        assert result == "fallback"
        assert se._degradation_count == 1

    def test_degradation_all_fail(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)

        def bad():
            raise ValueError("x")

        # all fallbacks fail; last_error is re-raised (not the unreachable RuntimeError)
        with pytest.raises(ValueError, match="x"):
            se.degrade(bad, [bad])

    def test_event_success_resets_circuit(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)
        cb = se._get_circuit_breaker("t1")
        cb._state = cb.__class__.__dict__  # use enum
        from cybernetics_agent.core.circuit_breaker import CircuitState
        cb._state = CircuitState.HALF_OPEN
        cb._success_count = 2  # one more success will close it (half_open_max_calls=3)
        event = CyberneticsEvent.create(
            EventType.TOOL_RESULT, "s",
            payload={"tool_name": "t1", "success": True},
        )
        se.on_event(event)
        assert cb._state == CircuitState.CLOSED

    def test_event_error_opens_circuit(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)
        cb = se._get_circuit_breaker("t1")
        cb._failure_count = 4
        event = CyberneticsEvent.create(
            EventType.TOOL_ERROR, "s",
            payload={"tool_name": "t1"},
        )
        se.on_event(event)
        assert cb._failure_count == 5

    def test_status_with_circuits(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)
        se._get_circuit_breaker("t1")
        status = se.get_status()
        assert "circuit_breakers" in status
        assert "t1" in status["circuit_breakers"]

    def test_status_without_circuits(self):
        ctx = MagicMock()
        se = StabilityEngine(
            config={"circuit_breaker": {"enabled": False}},
            ctx=ctx,
        )
        status = se.get_status()
        assert "circuit_breakers" not in status

    def test_reset_stats(self):
        ctx = MagicMock()
        se = StabilityEngine(config={}, ctx=ctx)
        se._retry_count = 5
        se._timeout_count = 3
        se.reset_stats()
        assert se._retry_count == 0
        assert se._timeout_count == 0
