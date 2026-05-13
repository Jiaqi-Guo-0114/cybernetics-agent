"""OptimalController 最终补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.optimal_controller import OptimalController


class TestOptimalControllerFinal:
    def test_tool_result_no_tool_name(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"duration": 1.0})
        oc.on_event(evt)

    def test_tool_error_no_tool_name(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {})
        oc.on_event(evt)

    def test_llm_request_no_model(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        oc.on_event(evt)

    def test_llm_response_no_model(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        oc.on_event(evt)

    def test_stage_transition_no_stages(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        oc.on_event(evt)

    def test_user_input_no_text(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        oc.on_event(evt)

    def test_user_feedback_no_type(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        oc.on_event(evt)

    def test_error_no_error_type(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        oc.on_event(evt)

    def test_can_afford(self):
        oc = OptimalController({}, None)
        result = oc.can_afford("test", 0.0)
        assert isinstance(result, bool)
