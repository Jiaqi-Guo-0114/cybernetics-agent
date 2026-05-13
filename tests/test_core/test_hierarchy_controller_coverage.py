"""HierarchyController 剩余代码补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.hierarchy_controller import HierarchyController
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestHierarchyControllerCoverage:
    def test_on_event_tool_call(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        hc.on_event(evt)

    def test_on_event_tool_result(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"})
        hc.on_event(evt)

    def test_on_event_tool_error(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"})
        hc.on_event(evt)

    def test_on_event_llm_request(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        hc.on_event(evt)

    def test_on_event_llm_response(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        hc.on_event(evt)

    def test_on_event_stage_transition(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        hc.on_event(evt)

    def test_on_event_user_input(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        hc.on_event(evt)

    def test_on_event_user_feedback(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        hc.on_event(evt)

    def test_on_event_error(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        hc.on_event(evt)

    def test_make_decision(self):
        hc = HierarchyController({}, None)
        d = hc.make_decision("layer1", "action", {"x": 1})
        assert d.layer == "layer1"

    def test_get_decision_chain(self):
        hc = HierarchyController({}, None)
        chain = hc.get_decision_chain()
        assert isinstance(chain, list)

    def test_get_layer_stats(self):
        hc = HierarchyController({}, None)
        stats = hc.get_layer_stats()
        assert isinstance(stats, dict)

    def test_reset(self):
        hc = HierarchyController({}, None)
        hc.reset()
