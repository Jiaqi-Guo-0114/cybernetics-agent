"""FeedbackLoop 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.feedback_loop import FeedbackLoop
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestFeedbackLoopFinal:
    def test_on_event_llm_request(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
        fl.on_event(evt)

    def test_on_event_llm_response(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"})
        fl.on_event(evt)

    def test_on_event_user_input(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {"text": "hello"})
        fl.on_event(evt)

    def test_on_event_stage_transition(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "s1", "to_stage": "s2"})
        fl.on_event(evt)

    def test_on_event_error(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {"error": "test"})
        fl.on_event(evt)

    def test_get_actions_after_events(self):
        fl = FeedbackLoop({}, None)
        for _ in range(5):
            fl.on_event(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"}))
            fl.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"}))
        actions = fl.get_actions()
        assert isinstance(actions, list)
