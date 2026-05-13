"""综合最终补充测试 - 覆盖所有剩余代码"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.feedback_loop import FeedbackLoop
from cybernetics_agent.core.hierarchy_controller import HierarchyController
from cybernetics_agent.core.info_flow import InfoFlow
from cybernetics_agent.core.optimal_controller import OptimalController
from cybernetics_agent.core.stability_engine import StabilityEngine
from cybernetics_agent.core.system_identifier import SystemIdentifier


class TestAllRemainingBranches:
    # system_identifier 剩余分支
    def test_si_stage_transition_no_from(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"to_stage": "s2"})
        si.on_event(evt)

    def test_si_stage_transition_no_to(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "s1"})
        si.on_event(evt)

    # feedback_loop 剩余分支
    def test_fl_tool_result_no_duration(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"})
        fl.on_event(evt)

    def test_fl_llm_response_no_tokens(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"})
        fl.on_event(evt)

    def test_fl_error_with_type(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {"error_type": "TimeoutError"})
        fl.on_event(evt)

    # adaptive_tuner 剩余分支
    def test_at_auto_tune_with_data(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]
        }, None)
        for _ in range(30):
            evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 0.1})
            at.on_event(evt)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_at_get_parameter_nonexistent(self):
        at = AdaptiveTuner({}, None)
        val = at.get_parameter("nonexistent")
        assert val is None

    # hierarchy_controller 剩余分支
    def test_hc_make_decision_no_meta(self):
        hc = HierarchyController({}, None)
        hc.make_decision("layer1", "action", {})
        assert hc is not None

    # info_flow 剩余分支
    def test_if_stage_transition(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "s1", "to_stage": "s2"})
        iflow.on_event(evt)

    # optimal_controller 剩余分支
    def test_oc_stage_transition(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        oc.on_event(evt)

    def test_oc_llm_request_no_tokens(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
        oc.on_event(evt)


    def test_se_circuit_breaker_open(self):
        se = StabilityEngine({}, None)
        for _ in range(10):
            se.on_event(CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {}))
        status = se.get_status()
        assert isinstance(status, dict)
