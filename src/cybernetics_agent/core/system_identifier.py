"""
系统辨识模块。

从事件流中提取规律，建立 "输入 → 输出" 的传递函数。
支持性能预测、转化漏斗分析、趋势识别。
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any

from .base import CyberneticsEvent, EventType, ICyberneticsModule


@dataclass
class StageMetrics:
    """单个阶段的性能指标。"""
    stage_name: str
    entry_count: int = 0
    exit_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    durations: list[float] = field(default_factory=list)

    @property
    def conversion_rate(self) -> float:
        if self.entry_count > 0:
            return self.exit_count / self.entry_count
        return 0.0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.error_count
        if total > 0:
            return self.success_count / total
        return 1.0

    @property
    def avg_duration(self) -> float:
        if self.durations:
            return statistics.mean(self.durations)
        return 0.0

    @property
    def p95_duration(self) -> float:
        if len(self.durations) >= 2:
            sorted_d = sorted(self.durations)
            idx = int(len(sorted_d) * 0.95)
            return sorted_d[min(idx, len(sorted_d) - 1)]
        return self.avg_duration


class SystemIdentifier(ICyberneticsModule):
    """
    系统辨识模块。

    核心能力：
    1. 采集 stage 间转化率
    2. 分析工具/模型的成功率和耗时分布
    3. 识别趋势和异常
    4. 基于历史数据预测未来性能

    配置示例（cybernetics.json）：
        "system_id": {
            "enabled": true,
            "metrics": ["conversion_rate", "latency", "error_rate"],
            "sampling_rate": 1.0,
            "retention_days": 30
        }
    """

    name = "system_id"

    def __init__(self, config: dict[str, Any], ctx: Any) -> None:
        super().__init__(config, ctx)
        self._metrics_list: list[str] = config.get("metrics", [
            "conversion_rate", "latency", "error_rate", "token_usage"
        ])
        self._sampling_rate: float = config.get("sampling_rate", 1.0)
        self._retention_days: int = config.get("retention_days", 30)

        # stage 性能数据
        self._stage_metrics: dict[str, StageMetrics] = {}
        # 工具性能数据: tool_name -> {calls, errors, durations}
        self._tool_stats: dict[str, dict[str, Any]] = {}
        # LLM 性能数据: model -> {calls, errors, prompt_tokens, completion_tokens}
        self._llm_stats: dict[str, dict[str, Any]] = {}

    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent | None:
        """收集事件并更新统计指标。"""
        et = event.event_type
        payload = event.payload

        if et == EventType.STAGE_TRANSITION:
            self._record_stage_transition(payload)

        elif et in (EventType.TOOL_RESULT, EventType.TOOL_ERROR):
            self._record_tool_event(payload, et == EventType.TOOL_ERROR)

        elif et in (EventType.LLM_RESPONSE, EventType.LLM_ERROR):
            self._record_llm_event(payload, et == EventType.LLM_ERROR)

        return event

    def _record_stage_transition(self, payload: dict[str, Any]) -> None:
        """记录阶段转化。"""
        stage = payload.get("stage", payload.get("to_stage", "unknown"))
        success = payload.get("success", True)
        duration = payload.get("duration", 0.0)

        if stage not in self._stage_metrics:
            self._stage_metrics[stage] = StageMetrics(stage_name=stage)

        sm = self._stage_metrics[stage]
        sm.entry_count += 1
        if success:
            sm.exit_count += 1
            sm.success_count += 1
        else:
            sm.error_count += 1

        if duration > 0:
            sm.total_duration += duration
            sm.durations.append(duration)
            # 保持列表不太长
            if len(sm.durations) > 1000:
                sm.durations = sm.durations[-500:]

    def _record_tool_event(self, payload: dict[str, Any], is_error: bool) -> None:
        """记录工具事件。"""
        tool_name = payload.get("tool_name", "unknown")
        duration = payload.get("duration", 0.0)

        if tool_name not in self._tool_stats:
            self._tool_stats[tool_name] = {
                "calls": 0, "errors": 0, "durations": []
            }

        stats = self._tool_stats[tool_name]
        stats["calls"] += 1
        if is_error:
            stats["errors"] += 1
        if duration > 0:
            stats["durations"].append(duration)
            if len(stats["durations"]) > 1000:
                stats["durations"] = stats["durations"][-500:]

    def _record_llm_event(self, payload: dict[str, Any], is_error: bool) -> None:
        """记录 LLM 事件。"""
        model = payload.get("model", "unknown")

        if model not in self._llm_stats:
            self._llm_stats[model] = {
                "calls": 0, "errors": 0,
                "prompt_tokens": 0, "completion_tokens": 0,
                "durations": []
            }

        stats = self._llm_stats[model]
        stats["calls"] += 1
        if is_error:
            stats["errors"] += 1
        stats["prompt_tokens"] += payload.get("prompt_tokens", 0)
        stats["completion_tokens"] += payload.get("completion_tokens", 0)

        duration = payload.get("duration", 0.0)
        if duration > 0:
            stats["durations"].append(duration)
            if len(stats["durations"]) > 1000:
                stats["durations"] = stats["durations"][-500:]

    def get_conversion_funnel(
        self,
        stages: list[str],
    ) -> dict[str, Any]:
        """
        计算转化漏斗。

        参数:
            stages: 阶段名称列表

        返回:
            {
                "stage0_to_stage1": 0.75,
                "stage1_to_stage2": 0.60,
                "overall": 0.45
            }
        """
        funnel: dict[str, Any] = {}

        for i in range(len(stages) - 1):
            from_stage = stages[i]
            to_stage = stages[i + 1]

            from_sm = self._stage_metrics.get(from_stage)
            to_sm = self._stage_metrics.get(to_stage)

            if from_sm and to_sm:
                rate = to_sm.entry_count / from_sm.entry_count if from_sm.entry_count > 0 else 0.0
            else:
                rate = 0.0

            funnel[f"{from_stage}_to_{to_stage}"] = round(rate, 4)

        # 整体转化率
        if len(stages) >= 2:
            first = self._stage_metrics.get(stages[0])
            last = self._stage_metrics.get(stages[-1])
            if first and last:
                overall = last.exit_count / first.entry_count if first.entry_count > 0 else 0.0
                funnel["overall"] = round(overall, 4)

        return funnel

    def predict_performance(
        self,
        query_type: str = "normal",
        expected_stages: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        基于历史数据预测性能。

        参数:
            query_type: 查询类型（宽泛/独立/正常）
            expected_stages: 预期的阶段列表

        返回:
            {
                "expected_duration": 300,
                "expected_success_rate": 0.85,
                "confidence": "medium",
                "bottleneck": "stage1"
            }
        """
        if not expected_stages:
            expected_stages = list(self._stage_metrics.keys())

        if not expected_stages:
            return {
                "expected_duration": 0,
                "expected_success_rate": 1.0,
                "confidence": "low",
                "bottleneck": None,
            }

        # 计算预期耗时
        total_duration = 0.0
        for stage in expected_stages:
            sm = self._stage_metrics.get(stage)
            if sm:
                total_duration += sm.avg_duration
            else:
                total_duration += 30.0  # 默认估计

        # 计算预期成功率（整体转化率乘积）
        overall_rate = 1.0
        for i in range(len(expected_stages) - 1):
            from_stage = expected_stages[i]
            to_stage = expected_stages[i + 1]
            from_sm = self._stage_metrics.get(from_stage)
            to_sm = self._stage_metrics.get(to_stage)

            if from_sm and to_sm and from_sm.entry_count > 0:
                rate = to_sm.entry_count / from_sm.entry_count
                overall_rate *= rate

        # 识别瓶颈（转化率最低的阶段）
        bottleneck = None
        min_rate = 1.0
        for i in range(len(expected_stages) - 1):
            from_stage = expected_stages[i]
            to_stage = expected_stages[i + 1]
            from_sm = self._stage_metrics.get(from_stage)
            to_sm = self._stage_metrics.get(to_stage)

            if from_sm and to_sm and from_sm.entry_count > 0:
                rate = to_sm.entry_count / from_sm.entry_count
                if rate < min_rate:
                    min_rate = rate
                    bottleneck = f"{from_stage}_to_{to_stage}"

        # 置信度
        total_samples = sum(
            sm.entry_count for sm in self._stage_metrics.values()
        )
        if total_samples > 100:
            confidence = "high"
        elif total_samples > 20:
            confidence = "medium"
        else:
            confidence = "low"

        # 查询类型调整
        if query_type == "broad":
            total_duration *= 1.5
            overall_rate *= 0.9
        elif query_type == "narrow":
            total_duration *= 0.7
            overall_rate *= 1.05

        return {
            "expected_duration": round(total_duration, 2),
            "expected_success_rate": round(min(overall_rate, 1.0), 4),
            "confidence": confidence,
            "bottleneck": bottleneck,
            "query_type": query_type,
        }

    def get_tool_performance(self, tool_name: str | None = None) -> dict[str, Any]:
        """获取工具性能数据。"""
        if tool_name:
            stats = self._tool_stats.get(tool_name)
            if not stats:
                return {}
            return {
                "tool": tool_name,
                "calls": stats["calls"],
                "errors": stats["errors"],
                "success_rate": (stats["calls"] - stats["errors"]) / stats["calls"] if stats["calls"] > 0 else 1.0,
                "avg_duration": statistics.mean(stats["durations"]) if stats["durations"] else 0.0,
            }

        return {
            name: self.get_tool_performance(name)
            for name in self._tool_stats
        }

    def get_status(self) -> dict[str, Any]:
        """获取模块状态。"""
        return {
            "enabled": self.enabled,
            "metrics_tracked": self._metrics_list,
            "stages_monitored": list(self._stage_metrics.keys()),
            "tools_monitored": list(self._tool_stats.keys()),
            "llm_models_monitored": list(self._llm_stats.keys()),
            "total_samples": sum(
                sm.entry_count for sm in self._stage_metrics.values()
            ),
            "stage_summary": {
                name: {
                    "entry_count": sm.entry_count,
                    "conversion_rate": round(sm.conversion_rate, 4),
                    "success_rate": round(sm.success_rate, 4),
                    "avg_duration": round(sm.avg_duration, 4),
                    "p95_duration": round(sm.p95_duration, 4),
                }
                for name, sm in self._stage_metrics.items()
            },
        }
