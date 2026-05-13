"""HierarchyController 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.hierarchy_controller import HierarchyController


class TestHierarchyControllerExtra:
    def test_on_event(self):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        hc.on_event(evt)

    def test_make_decision(self):
        hc = HierarchyController({}, None)
        d = hc.make_decision("layer1", "action", {"param": 1})
        assert d.layer == "layer1"
        assert d.decision_type == "action"

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

    def test_enabled_toggle(self):
        hc = HierarchyController({}, None)
        hc.enabled = False
        assert hc.enabled is False
        hc.enabled = True
        assert hc.enabled is True
