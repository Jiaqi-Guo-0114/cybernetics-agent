"""OptimalController 测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.optimal_controller import OptimalController
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestOptimalController:
    def test_init(self):
        oc = OptimalController({}, None)
        assert isinstance(oc.get_status(), dict)

    def test_initialize_shutdown(self):
        oc = OptimalController({}, None)
        oc.initialize()
        oc.shutdown()

    def test_on_event(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        result = oc.on_event(evt)
        assert result is not None

    def test_can_afford(self):
        oc = OptimalController({}, None)
        assert oc.can_afford("default", 0.0) is True

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

    def test_check_tool_concurrency(self):
        oc = OptimalController({}, None)
        assert isinstance(oc.check_tool_concurrency(), bool)

    def test_reset(self):
        oc = OptimalController({}, None)
        oc.reset()
