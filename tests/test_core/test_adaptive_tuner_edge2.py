"""AdaptiveTuner 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestAdaptiveTunerEdgeCases:
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

    def test_on_event_error(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        at.on_event(evt)

    def test_auto_tune_with_numeric(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]
        }, None)
        for _ in range(15):
            evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 0.1})
            at.on_event(evt)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_auto_tune_with_categorical(self):
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
