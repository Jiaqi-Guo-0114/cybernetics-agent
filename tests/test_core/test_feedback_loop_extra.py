"""FeedbackLoop 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.feedback_loop import FeedbackLoop
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestFeedbackLoopExtra:
    def test_on_event_tool_result(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"})
        fl.on_event(evt)

    def test_on_event_tool_error(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"})
        fl.on_event(evt)

    def test_on_event_user_feedback(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "correction", "text": "fix"})
        fl.on_event(evt)

    def test_get_actions(self):
        fl = FeedbackLoop({}, None)
        actions = fl.get_actions()
        assert isinstance(actions, list)

    def test_enabled_toggle(self):
        fl = FeedbackLoop({}, None)
        fl.enabled = False
        assert fl.enabled is False
        fl.enabled = True
        assert fl.enabled is True
