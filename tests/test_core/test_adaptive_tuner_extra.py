"""AdaptiveTuner 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType


class TestAdaptiveTunerExtra:
    def test_on_event_tool_result(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        at.on_event(evt)
        ranking = at.get_tool_ranking()
        assert isinstance(ranking, list)

    def test_on_event_tool_error(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"})
        at.on_event(evt)

    def test_on_event_user_feedback_correction(self):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 0}]}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "correction", "text": "别用 search"})
        at.on_event(evt)

    def test_on_event_user_input(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {"text": "研究论文"})
        at.on_event(evt)
        focus = at.get_topic_focus()
        assert isinstance(focus, list)

    def test_auto_tune_numeric(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "max_papers", "base": 10, "min": 3, "max": 50}]
        }, None)
        # 添加一些工具评分
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        at.on_event(evt)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_suggest_parameters(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "mode", "base": "normal", "options": ["slow", "normal", "fast"]}]
        }, None)
        suggestions = at.suggest_parameters()
        assert isinstance(suggestions, dict)

    def test_reset(self):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 0}]}, None)
        at.set_parameter("x", 10)
        at.reset()
        assert at.get_parameter("x") == 0
