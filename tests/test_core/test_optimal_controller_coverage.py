"""OptimalController 剩余代码补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.optimal_controller import OptimalController
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestOptimalControllerCoverage:
    def test_on_event_tool_call(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        oc.on_event(evt)

    def test_on_event_tool_result(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"})
        oc.on_event(evt)

    def test_on_event_tool_error(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"})
        oc.on_event(evt)

    def test_on_event_llm_request(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
        oc.on_event(evt)

    def test_on_event_llm_response(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"})
        oc.on_event(evt)

    def test_on_event_stage_transition(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        oc.on_event(evt)

    def test_on_event_user_input(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        oc.on_event(evt)

    def test_on_event_user_feedback(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        oc.on_event(evt)

    def test_on_event_error(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        oc.on_event(evt)

    def test_can_afford_no_pool(self):
        oc = OptimalController({}, None)
        assert oc.can_afford("nonexistent", 0.0) is True

    def test_get_budget_status(self):
        oc = OptimalController({}, None)
        status = oc.get_budget_status()
        assert isinstance(status, dict)

    def test_check_rate_limits(self):
        oc = OptimalController({}, None)
        assert isinstance(oc.check_llm_rate_limit(), bool)
        assert isinstance(oc.check_tool_concurrency(), bool)

    def test_get_fallback_strategy(self):
        oc = OptimalController({}, None)
        strategy = oc.get_fallback_strategy()
        assert isinstance(strategy, dict)
