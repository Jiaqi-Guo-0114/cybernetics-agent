"""HierarchyController 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.hierarchy_controller import HierarchyController
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestHierarchyControllerExtra:
    def test_on_event_llm_request(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        hc.on_event(evt)

    def test_on_event_user_input(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
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
