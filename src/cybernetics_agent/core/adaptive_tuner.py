"""
自适应调谐模块。

支持 EMA 滑动平均学习、参数动态调谐、用户行为追踪。
"""

from __future__ import annotations

import math
import time
from typing import Any

from .base import CyberneticsEvent, EventType, ICyberneticsModule
from .parameter_state import ParameterState


class AdaptiveTuner(ICyberneticsModule):
    """
    自适应调谐模块。

    核心能力：
    1. EMA 滑动平均学习（工具成功率、用户反馈等）
    2. 参数动态调谐（根据学习结果调整参数）
    3. 用户行为追踪（主题偏好、反馈评分）
    4. 用户纠正优先级最高

    配置示例（cybernetics.json）：
        "adaptive": {
            "enabled": true,
            "learning_rate": 0.3,
            "parameters": [
                {"name": "max_papers", "base": 10, "min": 3, "max": 50},
                {"name": "search_depth", "base": "normal", "options": ["shallow", "normal", "deep"]}
            ],
            "user_behavior": {
                "track_topics": true,
                "track_feedback": true
            }
        }
    """

    name = "adaptive"

    def __init__(self, config: dict[str, Any], ctx: Any) -> None:
        super().__init__(config, ctx)

        self._learning_rate = config.get("learning_rate", 0.3)

        # 参数配置
        self._parameters: dict[str, ParameterState] = {}
        for p in config.get("parameters", []):
            ps = ParameterState(
                name=p["name"],
                current_value=p.get("base"),
                base_value=p.get("base"),
                min_value=p.get("min"),
                max_value=p.get("max"),
                options=p.get("options", []),
                ema_value=0.5,  # 初始 EMA
            )
            self._parameters[p["name"]] = ps

        # 用户行为
        ub_config = config.get("user_behavior", {})
        self._track_topics = ub_config.get("track_topics", True)
        self._track_feedback = ub_config.get("track_feedback", True)
        self._topic_decay_days = ub_config.get("topic_decay_half_life_days", 7)

        # 学习状态
        self._tool_scores: dict[str, float] = {}  # tool_name -> EMA 得分
        self._topic_weights: dict[str, float] = {}  # topic -> 权重
        self._user_feedback: list[dict[str, Any]] = []
        self._banned_tools: set = set()

    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent | None:
        """处理事件，更新学习状态。"""
        et = event.event_type
        payload = event.payload

        if et == EventType.TOOL_RESULT:
            self._update_tool_score(payload)

        elif et == EventType.TOOL_ERROR:
            self._update_tool_score(payload, is_error=True)

        elif et == EventType.USER_FEEDBACK:
            self._process_user_feedback(payload)

        elif et == EventType.USER_INPUT and self._track_topics:
            self._extract_topics(payload.get("text", ""))

        return event

    def _update_tool_score(self, payload: dict[str, Any], is_error: bool = False) -> None:
        """更新工具的 EMA 得分。"""
        tool_name = payload.get("tool_name", "unknown")
        success = 0.0 if is_error else 1.0
        duration = payload.get("duration", 1.0)

        # 效率得分：耗时越短分越高
        efficiency = max(0.0, 1.0 - min(duration / 10.0, 1.0))

        # 综合得分：70% 成功率 + 30% 效率
        score = 0.7 * success + 0.3 * efficiency

        old_score = self._tool_scores.get(tool_name, 0.5)
        new_score = self._learning_rate * score + (1 - self._learning_rate) * old_score
        self._tool_scores[tool_name] = new_score

    def _process_user_feedback(self, payload: dict[str, Any]) -> None:
        """处理用户反馈。"""
        feedback_type = payload.get("type", "rating")

        if feedback_type == "rating":
            rating = payload.get("rating", 3)
            output_id = payload.get("output_id", "")

            self._user_feedback.append({
                "type": "rating",
                "rating": rating,
                "output_id": output_id,
                "timestamp": time.time(),
            })

            # 低分反馈 → 记录失败模式
            if rating <= 2:
                self._record_failure_pattern(output_id)

        elif feedback_type == "correction":
            correction = payload.get("text", "")
            self._user_feedback.append({
                "type": "correction",
                "text": correction,
                "timestamp": time.time(),
            })

            # 用户纠正优先级最高
            self._apply_user_correction(correction)

    def _record_failure_pattern(self, output_id: str) -> None:
        """记录失败模式。"""
        # 简单实现：记录到用户反馈中
        pass

    def _apply_user_correction(self, correction: str) -> None:
        """应用用户纠正。

        支持的纠正类型：
        - "别用 xxx" / "禁用 xxx" → 禁用工具
        - "多用 xxx" → 提高工具权重
        """
        correction_lower = correction.lower()

        # 检测禁用工具
        for tool_name in self._tool_scores:
            if f"别用 {tool_name}" in correction_lower or f"禁用 {tool_name}" in correction_lower:
                self._banned_tools.add(tool_name)
                self._tool_scores[tool_name] = 0.0

        # 检测提高工具权重
        for tool_name in self._tool_scores:
            if f"多用 {tool_name}" in correction_lower:
                self._tool_scores[tool_name] = min(1.0, self._tool_scores.get(tool_name, 0.5) + 0.2)

    def _extract_topics(self, text: str) -> None:
        """从用户输入中提取主题。"""
        # 简化实现：基于预定义词典映射
        topic_keywords = {
            "research": ["研究", "research", "paper", "论文"],
            "coding": ["代码", "coding", "programming", "编程"],
            "writing": ["写作", "writing", "draft", "草稿"],
            "analysis": ["分析", "analysis", "data", "数据"],
        }

        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    self._topic_weights[topic] = self._topic_weights.get(topic, 0) + 1
                    break

    def get_parameter(self, name: str) -> Any:
        """获取当前参数值。"""
        ps = self._parameters.get(name)
        if not ps:
            return None
        return ps.current_value

    def set_parameter(self, name: str, value: Any) -> None:
        """手动设置参数值。"""
        ps = self._parameters.get(name)
        if ps:
            ps.current_value = value
            ps.adjustment_count += 1

    def get_tool_ranking(self) -> list[tuple[str, float]]:
        """获取工具排名（按 EMA 得分从高到低）。"""
        scored = [
            (name, score)
            for name, score in self._tool_scores.items()
            if name not in self._banned_tools
        ]
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def get_topic_focus(self) -> list[tuple[str, float]]:
        """获取用户当前主题焦点。"""
        # 应用衰减
        now = time.time()
        decay_factor = math.exp(-math.log(2) / (self._topic_decay_days * 86400))
        time_diff = now - getattr(self, '_last_decay_time', now)
        self._last_decay_time = now

        for topic in list(self._topic_weights.keys()):
            self._topic_weights[topic] *= (decay_factor ** time_diff)
            if self._topic_weights[topic] < 0.1:
                del self._topic_weights[topic]

        total = sum(self._topic_weights.values()) or 1.0
        ranked = [
            (topic, weight / total)
            for topic, weight in self._topic_weights.items()
        ]
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def get_status(self) -> dict[str, Any]:
        """获取模块状态。"""
        return {
            "enabled": self.enabled,
            "learning_rate": self._learning_rate,
            "parameters": {
                name: {
                    "current": ps.current_value,
                    "base": ps.base_value,
                    "adjustments": ps.adjustment_count,
                }
                for name, ps in self._parameters.items()
            },
            "tool_scores": dict(self._tool_scores),
            "banned_tools": list(self._banned_tools),
            "tool_ranking": self.get_tool_ranking()[:5],
            "topic_focus": self.get_topic_focus()[:5],
            "recent_feedback_count": len(self._user_feedback),
        }

    def auto_tune(self) -> dict[str, Any]:
        """
        基于历史数据自动调整所有参数。

        返回调整日志，包含每个参数的旧值、新值和调整原因。
        """
        changes: dict[str, Any] = {}

        # 1. 数值型参数自动调整
        for name, ps in self._parameters.items():
            if isinstance(ps.base_value, (int, float)) and ps.min_value is not None and ps.max_value is not None:
                old_val = ps.current_value
                new_val = self._tune_numeric_parameter(name, ps)
                if new_val != old_val:
                    ps.current_value = new_val
                    ps.adjustment_count += 1
                    changes[name] = {
                        "old": old_val,
                        "new": new_val,
                        "reason": "auto_tune_numeric",
                    }

            # 2. 选项型参数自动调整
            elif ps.options:
                old_val = ps.current_value
                new_val = self._tune_option_parameter(name, ps)
                if new_val != old_val:
                    ps.current_value = new_val
                    ps.adjustment_count += 1
                    changes[name] = {
                        "old": old_val,
                        "new": new_val,
                        "reason": "auto_tune_option",
                    }

        # 3. 如果工具评分过低，自动放宽重试参数
        avg_tool_score = sum(self._tool_scores.values()) / len(self._tool_scores) if self._tool_scores else 0.5
        if avg_tool_score < 0.3:
            retry_param = self._parameters.get("max_retries")
            if retry_param and isinstance(retry_param.current_value, int):
                old_val = retry_param.current_value
                new_val = min(old_val + 1, 10)
                if new_val != old_val:
                    retry_param.current_value = new_val
                    retry_param.adjustment_count += 1
                    changes["max_retries"] = {
                        "old": old_val,
                        "new": new_val,
                        "reason": f"low_tool_score({avg_tool_score:.2f})",
                    }

        return changes

    def _tune_numeric_parameter(self, name: str, ps: ParameterState) -> Any:
        """
        调整数值型参数。

        策略：
        - 工具成功率高 → 提高并发/规模
        - 工具成功率低 → 降低并发/规模，增加保守性
        - 10% 概率做探索性尝试
        """
        import random

        # ε-greedy 探索
        if random.random() < 0.1:
            if isinstance(ps.base_value, int):
                return random.randint(int(ps.min_value), int(ps.max_value))
            return ps.min_value + random.random() * (ps.max_value - ps.min_value)

        avg_score = sum(self._tool_scores.values()) / len(self._tool_scores) if self._tool_scores else 0.5

        # 根据成功率调整
        current = ps.current_value
        if not isinstance(current, (int, float)):
            current = ps.base_value

        if avg_score > 0.7:
            # 成功率高，可以提高负载
            delta = (ps.max_value - ps.min_value) * 0.1 * self._learning_rate
            new_val = current + delta
        elif avg_score < 0.3:
            # 成功率低，降低负载
            delta = (ps.max_value - ps.min_value) * 0.1 * self._learning_rate
            new_val = current - delta
        else:
            # 成功率中等，向基准值回归
            new_val = current + (ps.base_value - current) * self._learning_rate * 0.3

        # 边界限制
        if isinstance(ps.base_value, int):
            return int(max(ps.min_value, min(ps.max_value, new_val)))
        return max(ps.min_value, min(ps.max_value, new_val))

    def _tune_option_parameter(self, name: str, ps: ParameterState) -> Any:
        """
        调整选项型参数。

        策略：
        - 高负载/成功率低 → 选择更保守的选项
        - 低负载/成功率高 → 选择更激进的选项
        """
        if not ps.options:
            return ps.current_value

        avg_score = sum(self._tool_scores.values()) / len(self._tool_scores) if self._tool_scores else 0.5

        # 简单策略：选项列表左侧更保守，右侧更激进
        idx = ps.options.index(ps.current_value) if ps.current_value in ps.options else len(ps.options) // 2

        if avg_score > 0.7 and idx < len(ps.options) - 1:
            return ps.options[idx + 1]  # 更激进
        elif avg_score < 0.3 and idx > 0:
            return ps.options[idx - 1]  # 更保守

        return ps.current_value

    def suggest_parameters(self) -> dict[str, dict[str, Any]]:
        """
        推荐参数调整方案（不应用）。

        返回每个参数的建议新值和理由。
        """
        suggestions: dict[str, dict[str, Any]] = {}

        for name, ps in self._parameters.items():
            if isinstance(ps.base_value, (int, float)) and ps.min_value is not None:
                suggested = self._tune_numeric_parameter(name, ps)
                if suggested != ps.current_value:
                    suggestions[name] = {
                        "current": ps.current_value,
                        "suggested": suggested,
                        "confidence": self._estimate_confidence(name),
                    }
            elif ps.options:
                suggested = self._tune_option_parameter(name, ps)
                if suggested != ps.current_value:
                    suggestions[name] = {
                        "current": ps.current_value,
                        "suggested": suggested,
                        "confidence": self._estimate_confidence(name),
                    }

        return suggestions

    def _estimate_confidence(self, name: str) -> float:
        """估计对某参数调整的置信度。

        基于已收集的样本数量：样本越多，置信度越高。
        """
        score_count = len(self._tool_scores)
        feedback_count = len(self._user_feedback)
        total_samples = score_count + feedback_count

        # 归一化到 0-1
        raw_confidence = min(total_samples / 20.0, 1.0)
        return round(raw_confidence, 2)

    def reset(self) -> None:
        """重置学习状态。"""
        self._tool_scores.clear()
        self._topic_weights.clear()
        self._user_feedback.clear()
        self._banned_tools.clear()
        for ps in self._parameters.values():
            ps.current_value = ps.base_value
            ps.ema_value = 0.5
            ps.adjustment_count = 0
