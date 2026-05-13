"""AdaptiveTuner 测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestAdaptiveTuner:
    def test_init(self):
        at = AdaptiveTuner({}, None)
        assert isinstance(at.get_status(), dict)

    def test_initialize_shutdown(self):
        at = AdaptiveTuner({}, None)
        at.initialize()
        at.shutdown()

    def test_on_event(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        result = at.on_event(evt)
        assert result is not None

    def test_set_get_parameter(self):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 0.0}]}, None)
        at.set_parameter("x", 1.0)
        assert at.get_parameter("x") == 1.0
        assert at.get_parameter("missing") is None

    def test_suggest_parameters(self):
        at = AdaptiveTuner({}, None)
        params = at.suggest_parameters()
        assert isinstance(params, dict)

    def test_auto_tune(self):
        at = AdaptiveTuner({}, None)
        result = at.auto_tune()
        assert isinstance(result, dict)

    def test_get_tool_ranking(self):
        at = AdaptiveTuner({}, None)
        ranking = at.get_tool_ranking()
        assert isinstance(ranking, list)

    def test_get_topic_focus(self):
        at = AdaptiveTuner({}, None)
        focus = at.get_topic_focus()
        assert isinstance(focus, list)

    def test_reset(self):
        at = AdaptiveTuner({}, None)
        at.reset()
