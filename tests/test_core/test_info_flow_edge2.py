"""InfoFlow 最终补充"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.info_flow import InfoFlow


class TestInfoFlowEdgeCases2:
    def test_on_event_llm_response(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        iflow.on_event(evt)

    def test_on_event_error(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        iflow.on_event(evt)

    def test_on_event_stage_transition(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        iflow.on_event(evt)

    def test_enabled_toggle(self):
        iflow = InfoFlow({}, None)
        iflow.enabled = False
        assert iflow.enabled is False
        iflow.enabled = True
        assert iflow.enabled is True
