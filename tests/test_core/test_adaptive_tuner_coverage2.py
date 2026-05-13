"""补齐 adaptive_tuner.py 未覆盖分支 — auto_tune、选项参数、置信度、主题衰减。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.base import CyberneticsEvent, EventType


class TestAdaptiveTunerBranches:
    def test_auto_tune_numeric_no_change(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "p1", "base": 10, "min": 1, "max": 20},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        # no tool scores, avg=0.5, current=base, tune returns same value
        # patch random to avoid epsilon-greedy exploration (10% chance)
        with patch("random.random", return_value=0.5):
            changes = at.auto_tune()
        assert "p1" not in changes

    def test_auto_tune_numeric_change(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "p1", "base": 10, "min": 1, "max": 100},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        # simulate high success rate
        at._tool_scores = {"t1": 0.9, "t2": 0.9}
        changes = at.auto_tune()
        assert "p1" in changes
        assert changes["p1"]["reason"] == "auto_tune_numeric"
        assert changes["p1"]["new"] > changes["p1"]["old"]

    def test_auto_tune_option_changes(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "depth", "base": "normal", "options": ["shallow", "normal", "deep"]},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        at._tool_scores = {"t1": 0.9}
        changes = at.auto_tune()
        assert changes["depth"]["new"] == "deep"

    def test_auto_tune_low_score_increases_retry(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "max_retries", "base": 2, "min": 1, "max": 10},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        at._tool_scores = {"t1": 0.1, "t2": 0.1}
        changes = at.auto_tune()
        # numeric tune first lowers from 2 to 1, then retry logic raises from 1 to 2
        assert changes["max_retries"]["new"] == 2
        assert "low_tool_score" in changes["max_retries"]["reason"]

    def test_auto_tune_option_no_change(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "depth", "base": "normal", "options": ["shallow", "normal", "deep"]},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        at._tool_scores = {"t1": 0.5}
        changes = at.auto_tune()
        assert "depth" not in changes

    def test_tune_numeric_epsilon_greedy_int(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "p1", "base": 10, "min": 0, "max": 100},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        with patch("random.random", return_value=0.05), patch("random.randint", return_value=42):
            result = at._tune_numeric_parameter("p1", at._parameters["p1"])
        assert result == 42

    def test_tune_numeric_epsilon_greedy_float(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "p1", "base": 10.5, "min": 0.0, "max": 100.0},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        with patch("random.random", return_value=0.05), patch("random.random", return_value=0.5):
            result = at._tune_numeric_parameter("p1", at._parameters["p1"])
        assert 0.0 <= result <= 100.0

    def test_tune_numeric_current_not_number(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "p1", "base": 10, "min": 0, "max": 100},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        at._parameters["p1"].current_value = "bad"
        at._tool_scores = {"t1": 0.9}
        result = at._tune_numeric_parameter("p1", at._parameters["p1"])
        assert isinstance(result, (int, float))

    def test_tune_numeric_float_boundary(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "p1", "base": 10.0, "min": 0.0, "max": 20.0},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        at._tool_scores = {"t1": 0.9}
        result = at._tune_numeric_parameter("p1", at._parameters["p1"])
        assert isinstance(result, float)
        assert 0.0 <= result <= 20.0

    def test_tune_option_no_options(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        from cybernetics_agent.core.parameter_state import ParameterState
        ps = ParameterState(name="x", current_value="a", base_value="a", options=[])
        assert at._tune_option_parameter("x", ps) == "a"

    def test_tune_option_high_score(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        from cybernetics_agent.core.parameter_state import ParameterState
        ps = ParameterState(name="x", current_value="normal", base_value="normal", options=["shallow", "normal", "deep"])
        at._tool_scores = {"t1": 0.9}
        assert at._tune_option_parameter("x", ps) == "deep"

    def test_tune_option_low_score(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        from cybernetics_agent.core.parameter_state import ParameterState
        ps = ParameterState(name="x", current_value="normal", base_value="normal", options=["shallow", "normal", "deep"])
        at._tool_scores = {"t1": 0.1}
        assert at._tune_option_parameter("x", ps) == "shallow"

    def test_suggest_parameters_numeric(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "p1", "base": 10, "min": 1, "max": 100},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        at._tool_scores = {"t1": 0.9}
        sug = at.suggest_parameters()
        assert "p1" in sug
        assert "confidence" in sug["p1"]

    def test_suggest_parameters_option(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "depth", "base": "normal", "options": ["shallow", "normal", "deep"]},
                ],
                "learning_rate": 0.3,
            },
            ctx=ctx,
        )
        at._tool_scores = {"t1": 0.9}
        sug = at.suggest_parameters()
        assert "depth" in sug

    def test_estimate_confidence(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        assert at._estimate_confidence("x") == 0.0
        at._tool_scores = {"a": 1.0, "b": 0.5}
        at._user_feedback = [{}, {}, {}]
        assert at._estimate_confidence("x") == 0.25
        for _ in range(20):
            at._user_feedback.append({})
        assert at._estimate_confidence("x") == 1.0

    def test_topic_decay_removes_low_weight(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        at._topic_weights["old"] = 0.05
        at._last_decay_time = 0
        focus = at.get_topic_focus()
        assert "old" not in [t for t, _ in focus]

    def test_topic_decay_keeps_high_weight(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        at._topic_weights["fresh"] = 5.0
        focus = at.get_topic_focus()
        assert focus[0][0] == "fresh"

    def test_user_feedback_rating_low(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.USER_FEEDBACK, "s",
            payload={"type": "rating", "rating": 1, "output_id": "out1"},
        )
        at.on_event(event)
        assert len(at._user_feedback) == 1

    def test_user_feedback_correction_ban(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        at._tool_scores = {"search": 0.5}
        event = CyberneticsEvent.create(
            EventType.USER_FEEDBACK, "s",
            payload={"type": "correction", "text": "禁用 search"},
        )
        at.on_event(event)
        assert "search" in at._banned_tools
        assert at._tool_scores["search"] == 0.0

    def test_user_feedback_correction_boost(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        at._tool_scores = {"search": 0.5}
        event = CyberneticsEvent.create(
            EventType.USER_FEEDBACK, "s",
            payload={"type": "correction", "text": "多用 search"},
        )
        at.on_event(event)
        assert at._tool_scores["search"] == 0.7

    def test_tool_ranking_excludes_banned(self):
        ctx = MagicMock()
        at = AdaptiveTuner(config={}, ctx=ctx)
        at._tool_scores = {"a": 0.9, "b": 0.8}
        at._banned_tools = {"a"}
        ranking = at.get_tool_ranking()
        assert ranking == [("b", 0.8)]

    def test_reset(self):
        ctx = MagicMock()
        at = AdaptiveTuner(
            config={
                "parameters": [
                    {"name": "p1", "base": 10},
                ],
            },
            ctx=ctx,
        )
        at._parameters["p1"].current_value = 99
        at._tool_scores = {"a": 1.0}
        at.reset()
        assert at._parameters["p1"].current_value == 10
        assert at._tool_scores == {}
