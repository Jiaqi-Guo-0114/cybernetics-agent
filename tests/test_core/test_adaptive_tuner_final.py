"""AdaptiveTuner 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestAdaptiveTunerFinal:
    def test_on_event_llm_request(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
        at.on_event(evt)

    def test_on_event_llm_response(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"})
        at.on_event(evt)

    def test_on_event_user_input(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {"text": "研究论文"})
        at.on_event(evt)

    def test_on_event_stage_transition(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        at.on_event(evt)

    def test_auto_tune_numeric(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]
        }, None)
        for _ in range(10):
            evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 0.1})
            at.on_event(evt)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_suggest_parameters(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]
        }, None)
        suggestions = at.suggest_parameters()
        assert isinstance(suggestions, dict)

    def test_tool_ranking_with_events(self):
        at = AdaptiveTuner({}, None)
        at.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}))
        ranking = at.get_tool_ranking()
        assert isinstance(ranking, list)
