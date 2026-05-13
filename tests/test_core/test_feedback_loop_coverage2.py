"""补齐 feedback_loop.py 未覆盖分支 — trigger 解析、深度限制、动作执行。"""

from __future__ import annotations

from unittest.mock import MagicMock

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.feedback_loop import FeedbackLoop


class TestFeedbackLoopBranches:
    def test_tool_result_failure_increments_error(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.TOOL_RESULT, "s",
            payload={"success": False},
        )
        fl.on_event(event)
        assert fl._tool_errors == 1
        assert fl._tool_calls == 1

    def test_max_depth_blocks_evaluation(self):
        ctx = MagicMock()
        fl = FeedbackLoop(
            config={"actions": [{"trigger": "tool_error_rate > 0", "action": "retry"}]},
            ctx=ctx,
        )
        fl._current_depth = 3
        fl._tool_errors = 1
        fl._tool_calls = 1
        fl._evaluate_rules()
        assert fl._current_depth == 3
        assert len(fl._action_history) == 0

    def test_trigger_no_regex_match(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        assert fl._evaluate_trigger("garbage", {"x": 1}) is False
        assert fl._evaluate_trigger("", {"x": 1}) is False

    def test_trigger_variable_not_in_context(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        assert fl._evaluate_trigger("missing > 0.5", {"other": 1}) is False

    def test_trigger_string_comparison(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        assert fl._evaluate_trigger('state == "ok"', {"state": "ok"}) is True
        assert fl._evaluate_trigger('state == "ok"', {"state": "bad"}) is False

    def test_trigger_unknown_operator(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        assert fl._evaluate_trigger("x <> 5", {"x": 5}) is False

    def test_trigger_type_error_comparison(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        # comparing str with float via > raises TypeError in Python 3
        assert fl._evaluate_trigger('state > 5', {"state": "abc"}) is False

    def test_trigger_all_operators(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        ctx_map = {"x": 5}
        assert fl._evaluate_trigger("x > 4", ctx_map) is True
        assert fl._evaluate_trigger("x >= 5", ctx_map) is True
        assert fl._evaluate_trigger("x < 6", ctx_map) is True
        assert fl._evaluate_trigger("x <= 5", ctx_map) is True
        assert fl._evaluate_trigger("x == 5", ctx_map) is True
        assert fl._evaluate_trigger("x != 6", ctx_map) is True

    def test_rule_triggers_action_and_emits(self):
        ctx = MagicMock()
        ctx.emit = MagicMock()
        ctx.session_id = "sess-01"
        fl = FeedbackLoop(
            config={
                "actions": [{"trigger": "tool_error_rate > 0.1", "action": "degrade"}],
                "max_feedback_depth": 3,
            },
            ctx=ctx,
        )
        fl._tool_errors = 1
        fl._tool_calls = 2
        fl._evaluate_rules()
        assert len(fl._action_history) == 1
        assert fl._action_history[0].action_type == "degrade"
        ctx.emit.assert_called_once()
        emitted = ctx.emit.call_args[0][0]
        assert emitted.payload["feedback_action"] == "degrade"
        assert emitted.payload["feedback_depth"] == 0
        assert fl._current_depth == 1

    def test_rule_trigger_once_per_eval(self):
        ctx = MagicMock()
        fl = FeedbackLoop(
            config={
                "actions": [
                    {"trigger": "tool_error_rate > 0", "action": "a1"},
                    {"trigger": "tool_error_rate > 0", "action": "a2"},
                ],
            },
            ctx=ctx,
        )
        fl._tool_errors = 1
        fl._tool_calls = 1
        fl._evaluate_rules()
        assert len(fl._action_history) == 1
        assert fl._action_history[0].action_type == "a1"

    def test_stage_transition_failure(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.STAGE_TRANSITION, "s",
            payload={"from_stage": "s1", "to_stage": "s2", "success": False},
        )
        fl.on_event(event)
        assert fl._stage_transitions["s1"]["total"] == 1
        assert fl._stage_transitions["s1"]["success"] == 0

    def test_stage_transition_success(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.STAGE_TRANSITION, "s",
            payload={"from_stage": "s1", "to_stage": "s2", "success": True},
        )
        fl.on_event(event)
        assert fl._stage_transitions["s1"]["success"] == 1

    def test_create_action_reason(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        from cybernetics_agent.core.feedback_loop import TriggerRule
        rule = TriggerRule(trigger="x>1", action="retry", params={"n": 2})
        action = fl._create_action(rule)
        assert action.action_type == "retry"
        assert action.params == {"n": 2}
        assert "Triggered by" in action.reason

    def test_execute_action_without_emit(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        from cybernetics_agent.core.feedback_loop import FeedbackAction
        action = FeedbackAction(action_type="abort")
        fl._execute_action(action)
        assert len(fl._action_history) == 1
        # ctx has no emit, so no call

    def test_mode_not_automatic(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": [], "mode": "manual"}, ctx=ctx)
        fl._tool_errors = 1
        fl._tool_calls = 1
        event = CyberneticsEvent.create(EventType.TOOL_ERROR, "s")
        fl.on_event(event)
        assert len(fl._action_history) == 0

    def test_get_actions_returns_copy(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        assert fl.get_actions() == []

    def test_reset_depth(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        fl._current_depth = 2
        fl.reset_depth()
        assert fl._current_depth == 0

    def test_build_context_zero_calls(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        ctx_map = fl._build_context()
        assert ctx_map["tool_error_rate"] == 0.0
        assert ctx_map["feedback_depth"] == 0.0

    def test_build_context_with_stages(self):
        ctx = MagicMock()
        fl = FeedbackLoop(config={"actions": []}, ctx=ctx)
        fl._stage_transitions = {
            "s1": {"total": 4, "success": 1},
        }
        ctx_map = fl._build_context()
        assert ctx_map["s1_failure_rate"] == 0.75
        assert ctx_map["s1_success_rate"] == 0.25
