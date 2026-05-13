"""InfoFlow 最终补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.info_flow import InfoFlow
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestInfoFlowFinal:
    def test_tool_result_no_tool_name(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"duration": 1.0})
        iflow.on_event(evt)

    def test_tool_error_no_tool_name(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {})
        iflow.on_event(evt)

    def test_llm_request_no_model(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        iflow.on_event(evt)

    def test_llm_response_no_model(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        iflow.on_event(evt)

    def test_stage_transition_no_stages(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        iflow.on_event(evt)

    def test_user_input_no_text(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        iflow.on_event(evt)

    def test_user_feedback_no_type(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        iflow.on_event(evt)

    def test_error_no_error_type(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        iflow.on_event(evt)

    def test_get_status(self):
        iflow = InfoFlow({}, None)
        status = iflow.get_status()
        assert isinstance(status, dict)
