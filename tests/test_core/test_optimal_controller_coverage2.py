"""补齐 optimal_controller.py 未覆盖分支 — 预算池边界、降级策略、成本估算。"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.optimal_controller import BudgetPool, OptimalController


class TestBudgetPoolBranches:
    def test_usage_rate_zero_allocated(self):
        pool = BudgetPool(name="test", allocated=0)
        assert pool.usage_rate == 0.0

    def test_reserve_failure(self):
        pool = BudgetPool(name="test", allocated=10, consumed=8)
        assert pool.reserve(5) is False
        assert pool.reserved == 0

    def test_reserve_success(self):
        pool = BudgetPool(name="test", allocated=10)
        assert pool.reserve(3) is True
        assert pool.reserved == 3
        assert pool.remaining == 7

    def test_release_does_not_go_negative(self):
        pool = BudgetPool(name="test", allocated=10, reserved=2)
        pool.release(5)
        assert pool.reserved == 0

    def test_consume_failure(self):
        pool = BudgetPool(name="test", allocated=5, consumed=4, reserved=1)
        assert pool.consume(1) is False


class TestOptimalControllerBranches:
    def test_estimate_cost_claude(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        cost = oc._estimate_cost({"model": "claude-3", "completion_tokens": 1000, "prompt_tokens": 1000})
        assert cost == 2000 / 1000 * 0.008

    def test_can_afford_missing_pool(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        assert oc.can_afford("missing", 100) is True

    def test_fallback_strategy_compress(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        oc._pools["tokens"].consumed = 95
        oc._pools["tokens"].allocated = 100
        strat = oc.get_fallback_strategy()
        types = [s["type"] for s in strat["strategies"]]
        assert "compress_context" in types

    def test_fallback_strategy_cheaper_model(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        oc._pools["tokens"].consumed = 75
        oc._pools["tokens"].allocated = 100
        strat = oc.get_fallback_strategy()
        types = [s["type"] for s in strat["strategies"]]
        assert "use_cheaper_model" in types
        assert "compress_context" not in types

    def test_fallback_strategy_batch(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        oc._pools["api_calls"].consumed = 85
        oc._pools["api_calls"].allocated = 100
        strat = oc.get_fallback_strategy()
        types = [s["type"] for s in strat["strategies"]]
        assert "batch_requests" in types

    def test_fallback_strategy_reduce_depth(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        oc._pools["cost_usd"].consumed = 85
        oc._pools["cost_usd"].allocated = 100
        strat = oc.get_fallback_strategy()
        types = [s["type"] for s in strat["strategies"]]
        assert "reduce_depth" in types

    def test_most_critical_pool(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        oc._pools["tokens"].consumed = 50
        oc._pools["api_calls"].consumed = 80
        assert oc._get_most_critical_pool() == "api_calls"

    def test_llm_request_cleans_old_times(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        import time
        oc._llm_request_times = [time.time() - 120, time.time() - 30]
        oc.on_event(CyberneticsEvent.create(
            EventType.LLM_REQUEST, "s",
            payload={"prompt_tokens": 10},
        ))
        assert len(oc._llm_request_times) == 2  # old removed, new added

    def test_check_llm_rate_limit_false(self):
        ctx = MagicMock()
        oc = OptimalController(
            config={"constraints": {"max_llm_requests_per_minute": 2}},
            ctx=ctx,
        )
        import time
        oc._llm_request_times = [time.time(), time.time()]
        assert oc.check_llm_rate_limit() is False

    def test_tool_result_decrements_active(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        oc._active_tools = 3
        oc.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s"))
        assert oc._active_tools == 2

    def test_tool_result_not_below_zero(self):
        ctx = MagicMock()
        oc = OptimalController(config={}, ctx=ctx)
        oc._active_tools = 0
        oc.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s"))
        assert oc._active_tools == 0
