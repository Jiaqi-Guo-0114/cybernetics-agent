"""FeedbackLoop 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.feedback_loop import FeedbackLoop
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestFeedbackLoopExtra:
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

    def test_get_actions_empty(self):
        fl = FeedbackLoop({}, None)
        actions = fl.get_actions()
        assert isinstance(actions, list)

    def test_reset_depth(self):
        fl = FeedbackLoop({}, None)
        fl.reset_depth()
