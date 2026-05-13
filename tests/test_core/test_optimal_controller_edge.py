"""OptimalController 边界条件测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.optimal_controller import OptimalController


class TestOptimalControllerEdgeCases:
    def test_on_event_tool_error(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search", "cost": 0.1})
        oc.on_event(evt)

    def test_on_event_unknown(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        oc.on_event(evt)

    def test_can_afford_no_budget(self):
        oc = OptimalController({}, None)
        assert oc.can_afford("nonexistent", 0.0) is True  # 无预算池时默认允许

    def test_check_llm_rate_limit_after_many(self):
        oc = OptimalController({}, None)
        for _ in range(100):
            evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
            oc.on_event(evt)
        assert isinstance(oc.check_llm_rate_limit(), bool)

    def test_check_tool_concurrency_after_many(self):
        oc = OptimalController({}, None)
        for _ in range(50):
            evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
            oc.on_event(evt)
        assert isinstance(oc.check_tool_concurrency(), bool)
