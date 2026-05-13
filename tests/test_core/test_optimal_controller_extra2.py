"""OptimalController 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.optimal_controller import OptimalController
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestOptimalControllerExtra:
    def test_on_event_llm_response(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4", "tokens": 50})
        oc.on_event(evt)

    def test_on_event_user_input(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        oc.on_event(evt)

    def test_can_afford_default(self):
        oc = OptimalController({}, None)
        assert oc.can_afford("default", 0.0) is True

    def test_get_budget_status(self):
        oc = OptimalController({}, None)
        status = oc.get_budget_status()
        assert isinstance(status, dict)

    def test_check_rate_limits(self):
        oc = OptimalController({}, None)
        assert isinstance(oc.check_llm_rate_limit(), bool)
        assert isinstance(oc.check_tool_concurrency(), bool)
