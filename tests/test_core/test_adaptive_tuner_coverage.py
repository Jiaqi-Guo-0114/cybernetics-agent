"""AdaptiveTuner 剩余代码补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestAdaptiveTunerCoverage:
    def test_on_event_tool_call(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        at.on_event(evt)

    def test_on_event_tool_result(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        at.on_event(evt)

    def test_on_event_tool_error(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"})
        at.on_event(evt)

    def test_on_event_llm_request(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
        at.on_event(evt)

    def test_on_event_llm_response(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"})
        at.on_event(evt)

    def test_on_event_stage_transition(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        at.on_event(evt)

    def test_on_event_user_input(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {"text": "hello"})
        at.on_event(evt)

    def test_on_event_user_feedback(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "correction"})
        at.on_event(evt)

    def test_on_event_error(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        at.on_event(evt)

    def test_auto_tune_with_numeric_param(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]
        }, None)
        for _ in range(20):
            evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 0.1})
            at.on_event(evt)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_auto_tune_with_categorical_param(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "mode", "base": "normal", "options": ["slow", "normal", "fast"]}]
        }, None)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_suggest_parameters(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]
        }, None)
        suggestions = at.suggest_parameters()
        assert isinstance(suggestions, dict)

    def test_get_tool_ranking(self):
        at = AdaptiveTuner({}, None)
        at.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}))
        ranking = at.get_tool_ranking()
        assert isinstance(ranking, list)

    def test_reset(self):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 0}]}, None)
        at.set_parameter("x", 10)
        at.reset()
        assert at.get_parameter("x") == 0
