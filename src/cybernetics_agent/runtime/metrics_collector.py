"""
指标采集器。

负责采集、汇总和分析系统运行指标。
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core.base import CyberneticsEvent


@dataclass
class MetricSnapshot:
    """单个时间点的指标快照。"""
    timestamp: float
    metric_name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    指标采集器。

    支持以下指标类型：
    - Counter: 累计计数（如总请求数）
    - Gauge: 即时值（如当前并发数）
    - Histogram: 分布（如响应时延）
    - Summary: 汇总（如成功率、转化率）

    使用示例:
        >>> collector = MetricsCollector()
        >>> collector.increment("tool_calls", labels={"tool": "search"})
        >>> collector.record("latency", 0.5, labels={"tool": "search"})
        >>> summary = collector.get_summary()
    """

    def __init__(self, event_store: Any | None = None) -> None:
        # Counter: metric_name -> {label_key: count}
        self._counters: dict[str, dict[str, int]] = {}
        # Gauge: metric_name -> {label_key: current_value}
        self._gauges: dict[str, dict[str, float]] = {}
        # Histogram: metric_name -> {label_key: [values]}
        self._histograms: dict[str, dict[str, list[float]]] = {}
        # 时间窗口：保留最近 N 条原始记录
        self._raw_events: list[dict[str, Any]] = []
        self._max_raw_events = 5000
        self._event_store = event_store

    def record_event(self, event: CyberneticsEvent) -> None:
        """
        从事件中自动提取指标。

        根据事件类型自动更新相关指标。
        """
        self._raw_events.append({
            "timestamp": event.timestamp,
            "event_type": event.event_type.value,
            "session_id": event.session_id,
            "payload": event.payload,
        })

        if len(self._raw_events) > self._max_raw_events:
            self._raw_events = self._raw_events[-self._max_raw_events // 2:]

        et = event.event_type
        payload = event.payload

        if et.value in ("tool_call", "tool_result", "tool_error"):
            tool_name = payload.get("tool_name", "unknown")
            self.increment("tool_calls_total", labels={"tool": tool_name})

            if et.value == "tool_error":
                self.increment("tool_errors_total", labels={"tool": tool_name})

            if "duration" in payload:
                self.record("tool_latency_seconds", payload["duration"], labels={"tool": tool_name})

        elif et.value in ("llm_request", "llm_response", "llm_error"):
            model = payload.get("model", "unknown")
            self.increment("llm_calls_total", labels={"model": model})

            if et.value == "llm_error":
                self.increment("llm_errors_total", labels={"model": model})

            if "duration" in payload:
                self.record("llm_latency_seconds", payload["duration"], labels={"model": model})

            if "prompt_tokens" in payload:
                self.increment("llm_tokens_total", labels={"model": model, "type": "prompt"})
            if "completion_tokens" in payload:
                self.increment("llm_tokens_total", labels={"model": model, "type": "completion"})

        elif et.value == "error":
            error_type = payload.get("error_type", "unknown")
            self.increment("errors_total", labels={"type": error_type})

        # 持久化到 SQLite
        if self._event_store is not None:
            with contextlib.suppress(Exception):
                self._event_store.write_event(
                    event_type=et.value,
                    payload=payload,
                    session_id=event.session_id,
                )

    def increment(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        """增加计数器。"""
        labels = labels or {}
        label_key = self._label_key(labels)

        if name not in self._counters:
            self._counters[name] = {}
        self._counters[name][label_key] = self._counters[name].get(label_key, 0) + value

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """设置仪表值。"""
        labels = labels or {}
        label_key = self._label_key(labels)

        if name not in self._gauges:
            self._gauges[name] = {}
        self._gauges[name][label_key] = value

    def record(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """记录到直方图。"""
        labels = labels or {}
        label_key = self._label_key(labels)

        if name not in self._histograms:
            self._histograms[name] = {}
        if label_key not in self._histograms[name]:
            self._histograms[name][label_key] = []
        self._histograms[name][label_key].append(value)

    def get_summary(self) -> dict[str, Any]:
        """
        获取指标汇总报告。

        返回包括计数器、仪表和直方图的统计信息。
        """
        summary: dict[str, Any] = {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {},
        }

        for name, label_data in self._histograms.items():
            summary["histograms"][name] = {}
            for label_key, values in label_data.items():
                if not values:
                    continue
                values_sorted = sorted(values)
                n = len(values_sorted)
                summary["histograms"][name][label_key] = {
                    "count": n,
                    "sum": sum(values_sorted),
                    "mean": sum(values_sorted) / n,
                    "min": values_sorted[0],
                    "max": values_sorted[-1],
                    "p50": values_sorted[n // 2],
                    "p95": values_sorted[int(n * 0.95)] if n >= 20 else values_sorted[-1],
                }

        # 计算成功率
        total_tools = sum(self._counters.get("tool_calls_total", {}).values())
        error_tools = sum(self._counters.get("tool_errors_total", {}).values())
        if total_tools > 0:
            summary["tool_success_rate"] = (total_tools - error_tools) / total_tools

        total_llm = sum(self._counters.get("llm_calls_total", {}).values())
        error_llm = sum(self._counters.get("llm_errors_total", {}).values())
        if total_llm > 0:
            summary["llm_success_rate"] = (total_llm - error_llm) / total_llm

        return summary

    def get_conversion_funnel(
        self,
        stages: list[str],
        session_id: str | None = None,
    ) -> dict[str, float]:
        """
        计算转化漏斗。

        参数:
            stages: 阶段名称列表，如 ["stage0", "stage1", "stage2"]
            session_id: 按 session 过滤

        返回:
            {"stage0_to_stage1": 0.75, "stage1_to_stage2": 0.60}
        """
        events = self._raw_events
        if session_id:
            events = [e for e in events if e.get("session_id") == session_id]

        stage_counts: dict[str, int] = {}
        for stage in stages:
            stage_counts[stage] = len([
                e for e in events
                if e.get("payload", {}).get("stage") == stage
                or e.get("event_type") == stage
            ])

        funnel: dict[str, float] = {}
        for i in range(len(stages) - 1):
            from_stage = stages[i]
            to_stage = stages[i + 1]
            from_count = stage_counts.get(from_stage, 0)
            to_count = stage_counts.get(to_stage, 0)

            if from_count > 0:
                key = f"{from_stage}_to_{to_stage}"
                funnel[key] = round(to_count / from_count, 4)

        return funnel

    def reset(self) -> None:
        """重置所有指标。"""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._raw_events.clear()

    @staticmethod
    def _label_key(labels: dict[str, str]) -> str:
        """将 label 字典转换为排序的字符串键。"""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def to_prometheus(self, prefix: str = "cybernetics") -> str:
        """
        导出 Prometheus 文本格式指标。

        返回的字符串可以直接作为 /metrics 端点响应。

        Args:
            prefix: 指标前缀，默认 "cybernetics"

        Returns:
            Prometheus 暴露格式字符串
        """
        lines: list[str] = []
        __import__("time").time()

        # Counter
        for name, label_data in self._counters.items():
            full_name = f"{prefix}_{name}"
            lines.append(f"# HELP {full_name} Auto-generated counter")
            lines.append(f"# TYPE {full_name} counter")
            for label_key, value in label_data.items():
                labels = self._parse_label_key(label_key)
                label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
                if label_str:
                    lines.append(f"{full_name}{{{label_str}}} {value}")
                else:
                    lines.append(f"{full_name} {value}")
            lines.append("")

        # Gauge
        for gname, gdata in self._gauges.items():
            full_name = f"{prefix}_{gname}"
            lines.append(f"# HELP {full_name} Auto-generated gauge")
            lines.append(f"# TYPE {full_name} gauge")
            for label_key, gvalue in gdata.items():
                glabels = self._parse_label_key(label_key)
                label_str = ",".join(f'{k}="{v}"' for k, v in sorted(glabels.items()))
                if label_str:
                    lines.append(f"{full_name}{{{label_str}}} {gvalue}")
                else:
                    lines.append(f"{full_name} {gvalue}")
            lines.append("")

        # Histogram
        buckets = [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")]
        for hname, hdata in self._histograms.items():
            full_name = f"{prefix}_{hname}"
            lines.append(f"# HELP {full_name} Auto-generated histogram")
            lines.append(f"# TYPE {full_name} histogram")
            for label_key, values in hdata.items():
                hlabels = self._parse_label_key(label_key)
                for bucket in buckets:
                    count = sum(1 for v in values if v <= bucket)
                    bucket_labels = dict(hlabels)
                    if bucket == float("inf"):
                        bucket_labels["le"] = "+Inf"
                    else:
                        bucket_labels["le"] = str(bucket)
                    label_str = ",".join(f'{k}="{v}"' for k, v in sorted(bucket_labels.items()))
                    lines.append(f"{full_name}_bucket{{{label_str}}} {count}")
                label_str = ",".join(f'{k}="{v}"' for k, v in sorted(hlabels.items()))
                if label_str:
                    lines.append(f"{full_name}_sum{{{label_str}}} {sum(values)}")
                    lines.append(f"{full_name}_count{{{label_str}}} {len(values)}")
                else:
                    lines.append(f"{full_name}_sum {sum(values)}")
                    lines.append(f"{full_name}_count {len(values)}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _parse_label_key(label_key: str) -> dict[str, str]:
        """将 label 字符串键解析回字典。"""
        result: dict[str, str] = {}
        if not label_key:
            return result
        for part in label_key.split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                result[k] = v
        return result

    def to_openmetrics(self, prefix: str = "cybernetics") -> str:
        """
        导出 OpenMetrics 格式（Prometheus 超集）。

        与 Prometheus 格式类似，但在末尾添加 EOF 标记。
        """
        return self.to_prometheus(prefix) + "\n# EOF\n"
