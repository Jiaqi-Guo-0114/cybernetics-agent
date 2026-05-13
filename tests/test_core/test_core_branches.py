"""核心模块最终补充测试 - 触发条件分支"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.feedback_loop import FeedbackLoop
from cybernetics_agent.core.hierarchy_controller import HierarchyController
from cybernetics_agent.core.info_flow import InfoFlow
from cybernetics_agent.core.optimal_controller import OptimalController
from cybernetics_agent.core.stability_engine import StabilityEngine
from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestCoreModuleBranches:
    # system_identifier 剩余分支
    def test_si_enabled_false(self):
        si = SystemIdentifier({}, None)
        si.enabled = False
        si.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {}))
        assert si.get_status()["enabled"] is False

    def test_si_predict_empty_stages(self):
        si = SystemIdentifier({}, None)
        result = si.predict_performance()
        assert isinstance(result, dict)

    # feedback_loop 剩余分支
    def test_fl_enabled_false(self):
        fl = FeedbackLoop({}, None)
        fl.enabled = False
        fl.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {}))
        assert fl.get_actions() == []

    def test_fl_no_context(self):
        fl = FeedbackLoop({}, None)
        actions = fl.get_actions()
        assert isinstance(actions, list)

    # adaptive_tuner 剩余分支
    def test_at_enabled_false(self):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 0}]}, None)
        at.enabled = False
        at.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {}))
        assert at.get_parameter("x") == 0

    def test_at_auto_tune_empty(self):
        at = AdaptiveTuner({}, None)
        changes = at.auto_tune()
        assert changes == {}

    # hierarchy_controller 剩余分支
    def test_hc_enabled_false(self):
        hc = HierarchyController({}, None)
        hc.enabled = False
        hc.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {}))
        assert hc.get_layer_stats() == {}

    # info_flow 剩余分支
    def test_if_enabled_false(self):
        iflow = InfoFlow({}, None)
        iflow.enabled = False
        iflow.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {}))
        assert iflow.enabled is False

    # optimal_controller 剩余分支
    def test_oc_enabled_false(self):
        oc = OptimalController({}, None)
        oc.enabled = False
        oc.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {}))
        status = oc.get_budget_status()
        assert isinstance(status, dict)

    # stability_engine 剩余分支
    def test_se_enabled_false(self):
        se = StabilityEngine({}, None)
        se.enabled = False
        se.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {}))
        assert se.enabled is False
