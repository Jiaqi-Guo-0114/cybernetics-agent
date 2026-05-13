"""HierarchyController 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.hierarchy_controller import HierarchyController
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestHierarchyControllerEdgeCases:
    def test_on_event_llm_response(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        hc.on_event(evt)

    def test_on_event_error(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        hc.on_event(evt)

    def test_make_decision_with_data(self):
        hc = HierarchyController({}, None)
        d = hc.make_decision("layer1", "action", {"param": 1})
        assert d.layer == "layer1"

    def test_get_decision_chain_with_layer(self):
        hc = HierarchyController({}, None)
        hc.make_decision("layer1", "action", {})
        chain = hc.get_decision_chain("layer1")
        assert isinstance(chain, list)

    def test_reset(self):
        hc = HierarchyController({}, None)
        hc.reset()
