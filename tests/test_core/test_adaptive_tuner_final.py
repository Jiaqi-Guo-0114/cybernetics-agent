"""AdaptiveTuner 最终补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestAdaptiveTunerFinal:
    def test_tool_result_no_tool_name(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"duration": 1.0})
        at.on_event(evt)

    def test_tool_error_no_tool_name(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {})
        at.on_event(evt)

    def test_llm_request_no_model(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        at.on_event(evt)

    def test_llm_response_no_model(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        at.on_event(evt)

    def test_user_feedback_no_type(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        at.on_event(evt)

    def test_auto_tune_empty(self):
        at = AdaptiveTuner({}, None)
        changes = at.auto_tune()
        assert changes == {}


    def test_get_tool_ranking_empty(self):
        at = AdaptiveTuner({}, None)
        ranking = at.get_tool_ranking()
        assert ranking == []
