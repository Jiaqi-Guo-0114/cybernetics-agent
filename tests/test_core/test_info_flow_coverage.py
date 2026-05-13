"""InfoFlow 剩余代码补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.info_flow import InfoFlow
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestInfoFlowCoverage:
    def test_on_event_tool_call(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        iflow.on_event(evt)

    def test_on_event_tool_result(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"})
        iflow.on_event(evt)

    def test_on_event_tool_error(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"})
        iflow.on_event(evt)

    def test_on_event_llm_request(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        iflow.on_event(evt)

    def test_on_event_llm_response(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        iflow.on_event(evt)

    def test_on_event_stage_transition(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        iflow.on_event(evt)

    def test_on_event_user_input(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        iflow.on_event(evt)

    def test_on_event_user_feedback(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        iflow.on_event(evt)

    def test_on_event_error(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        iflow.on_event(evt)

    def test_initialize(self):
        iflow = InfoFlow({}, None)
        iflow.initialize()

    def test_shutdown(self):
        iflow = InfoFlow({}, None)
        iflow.shutdown()
