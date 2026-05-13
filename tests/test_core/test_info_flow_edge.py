"""InfoFlow 边界条件测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.info_flow import InfoFlow
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestInfoFlowEdgeCases:
    def test_on_event_llm_request(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        iflow.on_event(evt)

    def test_on_event_unknown(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        iflow.on_event(evt)
