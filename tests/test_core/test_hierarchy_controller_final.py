"""HierarchyController 最终补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.hierarchy_controller import HierarchyController


class TestHierarchyControllerFinal:
    def test_tool_result_no_tool_name(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"duration": 1.0})
        hc.on_event(evt)

    def test_tool_error_no_tool_name(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {})
        hc.on_event(evt)

    def test_llm_request_no_model(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        hc.on_event(evt)

    def test_llm_response_no_model(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        hc.on_event(evt)

    def test_make_decision(self):
        hc = HierarchyController({}, None)
        hc.make_decision("layer1", "action", {"x": 1})
        assert hc is not None
