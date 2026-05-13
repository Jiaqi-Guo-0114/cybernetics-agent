"""AdaptiveTuner 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType


class TestAdaptiveTunerExtra2:
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

    def test_auto_tune_with_params(self):
        at = AdaptiveTuner({
            "parameters": [
                {"name": "x", "base": 10, "min": 1, "max": 100},
                {"name": "mode", "base": "normal", "options": ["slow", "normal", "fast"]}
            ]
        }, None)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_suggest_with_params(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]
        }, None)
        suggestions = at.suggest_parameters()
        assert isinstance(suggestions, dict)

    def test_reset(self):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 0}]}, None)
        at.set_parameter("x", 10)
        at.reset()
        assert at.get_parameter("x") == 0
