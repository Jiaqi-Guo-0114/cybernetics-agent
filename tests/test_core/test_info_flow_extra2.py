"""InfoFlow 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.info_flow import InfoFlow
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestInfoFlowExtra:
    def test_on_event_llm_request(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        iflow.on_event(evt)

    def test_on_event_llm_response(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        iflow.on_event(evt)

    def test_on_event_user_input(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        iflow.on_event(evt)

    def test_initialize_shutdown(self):
        iflow = InfoFlow({}, None)
        iflow.initialize()
        iflow.shutdown()
