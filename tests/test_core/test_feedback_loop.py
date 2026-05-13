"""FeedbackLoop 测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.feedback_loop import FeedbackLoop


class TestFeedbackLoop:
    def test_init(self):
        fl = FeedbackLoop({}, None)
        assert isinstance(fl.get_status(), dict)

    def test_on_event(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        result = fl.on_event(evt)
        assert result is not None

    def test_initialize_shutdown(self):
        fl = FeedbackLoop({}, None)
        fl.initialize()
        fl.shutdown()

    def test_get_actions(self):
        fl = FeedbackLoop({}, None)
        actions = fl.get_actions()
        assert isinstance(actions, list)

    def test_reset_depth(self):
        fl = FeedbackLoop({}, None)
        fl.reset_depth()
