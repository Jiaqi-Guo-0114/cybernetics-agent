"""AdaptiveTuner 边界条件测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestAdaptiveTunerEdgeCases:
    def test_on_event_user_feedback_rating_low(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "rating", "rating": 1})
        at.on_event(evt)

    def test_on_event_user_feedback_rating_high(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "rating", "rating": 5})
        at.on_event(evt)

    def test_on_event_unknown(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        at.on_event(evt)

    def test_auto_tune_with_high_score(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "max_papers", "base": 10, "min": 3, "max": 50}]
        }, None)
        # 多次成功提高工具评分
        for _ in range(20):
            evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 0.1})
            at.on_event(evt)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_auto_tune_with_low_score(self):
        at = AdaptiveTuner({
            "parameters": [{"name": "max_papers", "base": 10, "min": 3, "max": 50}]
        }, None)
        # 多次失败降低工具评分
        for _ in range(20):
            evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"})
            at.on_event(evt)
        changes = at.auto_tune()
        assert isinstance(changes, dict)

    def test_suggest_parameters_no_changes(self):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 0}]}, None)
        suggestions = at.suggest_parameters()
        assert isinstance(suggestions, dict)

    def test_get_topic_focus_empty(self):
        at = AdaptiveTuner({}, None)
        focus = at.get_topic_focus()
        assert focus == []

    def test_tool_ranking_with_banned(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        at.on_event(evt)
        # 禁用工具
        at._banned_tools.add("search")
        ranking = at.get_tool_ranking()
        assert "search" not in [r[0] for r in ranking]

    def test_user_correction_ban(self):
        at = AdaptiveTuner({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        at.on_event(evt)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "correction", "text": "禁用 search"})
        at.on_event(evt)
        assert "search" in at._banned_tools
