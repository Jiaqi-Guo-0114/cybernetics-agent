"""HierarchyController 边界条件测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.hierarchy_controller import HierarchyController
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestHierarchyControllerEdgeCases:
    def test_on_event_llm_request(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        hc.on_event(evt)

    def test_on_event_unknown(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        hc.on_event(evt)

    def test_make_decision_multiple(self):
        hc = HierarchyController({}, None)
        hc.make_decision("layer1", "action", {"x": 1})
        hc.make_decision("layer1", "action", {"x": 2})
        chain = hc.get_decision_chain("layer1")
        assert len(chain) >= 1

    def test_get_decision_chain_since(self):
        hc = HierarchyController({}, None)
        import time
        t0 = time.time()
        hc.make_decision("layer1", "action", {})
        chain = hc.get_decision_chain(since=t0 - 1)
        assert len(chain) >= 1
