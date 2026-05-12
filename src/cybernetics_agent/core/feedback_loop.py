"""
反馈闭环模块。

实现 "检测→决策→行动" 的真闭环。
监听事件流，根据配置规则自动触发调整动作。
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base import CyberneticsEvent, EventType, ICyberneticsModule


@dataclass
class FeedbackAction:
    """反馈动作。"""
    action_type: str  # "retry", "degrade", "adjust", "abort", "proceed"
    params: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class TriggerRule:
    """触发规则。"""
    trigger: str  # 如 "tool_error_rate > 0.3"
    action: str   # 如 "retry_with_deeper_model"
    params: Dict[str, Any] = field(default_factory=dict)


class FeedbackLoop(ICyberneticsModule):
    """
    反馈闭环模块。

    核心逻辑：
    1. 收集事件（工具调用结果、错误、用户反馈等）
    2. 计算实时指标（失败率、超时率等）
    3. 匹配触发规则
    4. 生成并执行反馈动作
    5. 记录反馈历史，防止无限循环

    配置示例（cybernetics.json）：
        "feedback_loop": {
            "enabled": true,
            "mode": "automatic",
            "actions": [
                {"trigger": "tool_error_rate > 0.3", "action": "retry"},
                {"trigger": "stage_failure_rate > 0.5", "action": "degrade"}
            ],
            "max_feedback_depth": 3
        }
    """

    name = "feedback_loop"

    def __init__(self, config: Dict[str, Any], ctx: Any) -> None:
        super().__init__(config, ctx)
        self._rules: List[TriggerRule] = []
        self._action_history: List[FeedbackAction] = []
        self._current_depth = 0
        self._max_depth = config.get("max_feedback_depth", 3)
        self._mode = config.get("mode", "automatic")

        # 实时指标统计
        self._tool_calls = 0
        self._tool_errors = 0
        self._stage_transitions: Dict[str, Dict[str, int]] = {}

        # 解析配置规则
        for rule_data in config.get("actions", []):
            self._rules.append(TriggerRule(
                trigger=rule_data["trigger"],
                action=rule_data["action"],
                params=rule_data.get("params", {}),
            ))

    def on_event(self, event: CyberneticsEvent) -> Optional[CyberneticsEvent]:
        """
        处理事件，更新指标并检查触发条件。
        """
        et = event.event_type

        # 更新实时指标
        if et == EventType.TOOL_RESULT:
            self._tool_calls += 1
            if not event.payload.get("success", True):
                self._tool_errors += 1

        elif et == EventType.TOOL_ERROR:
            self._tool_calls += 1
            self._tool_errors += 1

        elif et == EventType.STAGE_TRANSITION:
            from_stage = event.payload.get("from_stage", "unknown")
            to_stage = event.payload.get("to_stage", "unknown")
            success = event.payload.get("success", True)

            if from_stage not in self._stage_transitions:
                self._stage_transitions[from_stage] = {"total": 0, "success": 0}
            self._stage_transitions[from_stage]["total"] += 1
            if success:
                self._stage_transitions[from_stage]["success"] += 1

        # 检查触发规则
        if self._mode == "automatic":
            self._evaluate_rules()

        return event

    def _evaluate_rules(self) -> None:
        """评估所有规则，触发符合条件的动作。"""
        if self._current_depth >= self._max_depth:
            return

        context = self._build_context()

        for rule in self._rules:
            if self._evaluate_trigger(rule.trigger, context):
                action = self._create_action(rule)
                self._execute_action(action)
                self._current_depth += 1
                break  # 一次只触发一个动作

    def _build_context(self) -> Dict[str, float]:
        """构建评估上下文。"""
        ctx: Dict[str, float] = {}

        # 工具错误率
        if self._tool_calls > 0:
            ctx["tool_error_rate"] = self._tool_errors / self._tool_calls
        else:
            ctx["tool_error_rate"] = 0.0

        # 阶段失败率
        for stage, counts in self._stage_transitions.items():
            total = counts["total"]
            if total > 0:
                ctx[f"{stage}_failure_rate"] = 1.0 - (counts["success"] / total)
                ctx[f"{stage}_success_rate"] = counts["success"] / total

        # 反馈深度
        ctx["feedback_depth"] = float(self._current_depth)

        return ctx

    def _evaluate_trigger(self, trigger: str, context: Dict[str, float]) -> bool:
        """
        评估单个触发条件。

        支持的表达式格式：
            "tool_error_rate > 0.3"
            "stage0_failure_rate >= 0.5"
            "feedback_depth < 3"
        """
        # 解析表达式：variable operator value
        match = re.match(r"(.+?)\s*(>=|<=|>|<|==|!=)\s*(.+)", trigger.strip())
        if not match:
            return False

        var_name, operator, value_str = match.groups()
        var_name = var_name.strip()
        value_str = value_str.strip()

        # 获取变量值
        if var_name not in context:
            return False
        var_value = context[var_name]

        # 解析比较值
        try:
            compare_value = float(value_str)
        except ValueError:
            compare_value = value_str.strip('"').strip("'")

        # 执行比较
        ops = {
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }

        op_func = ops.get(operator)
        if not op_func:
            return False

        try:
            return bool(op_func(var_value, compare_value))
        except (TypeError, ValueError):
            return False

    def _create_action(self, rule: TriggerRule) -> FeedbackAction:
        """根据规则创建动作。"""
        return FeedbackAction(
            action_type=rule.action,
            params=rule.params,
            reason=f"Triggered by: {rule.trigger}",
        )

    def _execute_action(self, action: FeedbackAction) -> None:
        """执行反馈动作。"""
        self._action_history.append(action)

        # 发射反馈事件到事件总线
        if hasattr(self.ctx, "emit"):
            from .base import CyberneticsEvent
            feedback_event = CyberneticsEvent.create(
                event_type=EventType.CUSTOM,
                session_id=getattr(self.ctx, "session_id", "unknown"),
                payload={
                    "feedback_action": action.action_type,
                    "feedback_params": action.params,
                    "feedback_reason": action.reason,
                    "feedback_depth": self._current_depth,
                },
                metadata={"source": "feedback_loop"},
            )
            self.ctx.emit(feedback_event)

    def get_status(self) -> Dict[str, Any]:
        """获取模块状态。"""
        return {
            "enabled": self.enabled,
            "mode": self._mode,
            "rules_count": len(self._rules),
            "current_depth": self._current_depth,
            "max_depth": self._max_depth,
            "tool_calls": self._tool_calls,
            "tool_errors": self._tool_errors,
            "tool_error_rate": self._tool_errors / self._tool_calls if self._tool_calls > 0 else 0.0,
            "stage_transitions": self._stage_transitions,
            "recent_actions": [
                {
                    "type": a.action_type,
                    "reason": a.reason,
                    "timestamp": a.timestamp,
                }
                for a in self._action_history[-5:]
            ],
        }

    def get_actions(self) -> List[FeedbackAction]:
        """获取所有历史反馈动作。"""
        return list(self._action_history)

    def reset_depth(self) -> None:
        """重置反馈深度计数器。

        在新的任务/会话开始时调用。
        """
        self._current_depth = 0
