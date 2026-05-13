"""OptimalController 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.optimal_controller import BudgetPool, OptimalController


class TestOptimalControllerExtra:
    def test_on_event_tool_result(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "cost": 0.1})
        oc.on_event(evt)

    def test_on_event_llm_request(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4", "tokens": 100})
        oc.on_event(evt)

    def test_can_afford_true(self):
        oc = OptimalController({}, None)
        assert oc.can_afford("llm", 0.0) is True

    def test_get_budget_status(self):
        oc = OptimalController({}, None)
        status = oc.get_budget_status()
        assert isinstance(status, dict)

    def test_get_fallback_strategy(self):
        oc = OptimalController({}, None)
        strategy = oc.get_fallback_strategy()
        assert isinstance(strategy, dict)

    def test_check_llm_rate_limit(self):
        oc = OptimalController({}, None)
        assert isinstance(oc.check_llm_rate_limit(), bool)

    def test_budget_pool(self):
        pool = BudgetPool("test", 100.0)
        assert pool.name == "test"
        assert pool.remaining == 100.0

    def test_budget_pool_consume(self):
        pool = BudgetPool("test", 100.0)
        assert pool.consume(50.0) is True
        assert pool.remaining == 50.0
        assert pool.consume(60.0) is False
