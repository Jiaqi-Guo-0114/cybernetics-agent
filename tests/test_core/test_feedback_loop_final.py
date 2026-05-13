"""FeedbackLoop 最终补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.feedback_loop import FeedbackLoop


class TestFeedbackLoopFinal:
    def test_tool_result_no_tool_name(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"duration": 1.0})
        fl.on_event(evt)

    def test_tool_error_no_tool_name(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {})
        fl.on_event(evt)

    def test_llm_request_no_model(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        fl.on_event(evt)

    def test_llm_response_no_model(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        fl.on_event(evt)

    def test_stage_transition_no_stages(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        fl.on_event(evt)

    def test_user_input_no_text(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        fl.on_event(evt)

    def test_user_feedback_no_type(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        fl.on_event(evt)

    def test_error_no_error_type(self):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        fl.on_event(evt)

    def test_get_actions_empty(self):
        fl = FeedbackLoop({}, None)
        actions = fl.get_actions()
        assert isinstance(actions, list)

    def test_context_limit(self):
        fl = FeedbackLoop({"max_feedback_depth": 2}, None)
        for _i in range(10):
            fl.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"}))
        actions = fl.get_actions()
        assert isinstance(actions, list)
