"""
指标采集器。

负责采集、汇总和分析系统运行指标。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..core.base import CyberneticsEvent


@dataclass
class MetricSnapshot:
    """单个时间点的指标快照。"""
    timestamp: float
    metric_name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


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

    def __init__(self) -> None:
        # Counter: metric_name -> {label_key: count}
        self._counters: Dict[str, Dict[str, int]] = {}
        # Gauge: metric_name -> {label_key: current_value}
        self._gauges: Dict[str, Dict[str, float]] = {}
        # Histogram: metric_name -> {label_key: [values]}
        self._histograms: Dict[str, Dict[str, List[float]]] = {}
        # 时间窗口：保留最近 N 条原始记录
        self._raw_events: List[Dict[str, Any]] = []
        self._max_raw_events = 5000

    def record_event(self, event: "CyberneticsEvent") -> None:
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

    def increment(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> None:
        """增加计数器。"""
        labels = labels or {}
        label_key = self._label_key(labels)

        if name not in self._counters:
            self._counters[name] = {}
        self._counters[name][label_key] = self._counters[name].get(label_key, 0) + value

    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """设置仪表值。"""
        labels = labels or {}
        label_key = self._label_key(labels)

        if name not in self._gauges:
            self._gauges[name] = {}
        self._gauges[name][label_key] = value

    def record(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """记录到直方图。"""
        labels = labels or {}
        label_key = self._label_key(labels)

        if name not in self._histograms:
            self._histograms[name] = {}
        if label_key not in self._histograms[name]:
            self._histograms[name][label_key] = []
        self._histograms[name][label_key].append(value)

    def get_summary(self) -> Dict[str, Any]:
        """
        获取指标汇总报告。

        返回包括计数器、仪表和直方图的统计信息。
        """
        summary: Dict[str, Any] = {
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
        stages: List[str],
        session_id: Optional[str] = None,
    ) -> Dict[str, float]:
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

        stage_counts: Dict[str, int] = {}
        for stage in stages:
            stage_counts[stage] = len([
                e for e in events
                if e.get("payload", {}).get("stage") == stage
                or e.get("event_type") == stage
            ])

        funnel: Dict[str, float] = {}
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
    def _label_key(labels: Dict[str, str]) -> str:
        """将 label 字典转换为排序的字符串键。"""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/runtime", 1)[0])
    from core.base import CyberneticsEvent, EventType

    # 测试 1: 基本计数
    collector = MetricsCollector()
    collector.increment("requests", labels={"method": "GET"})
    collector.increment("requests", value=2, labels={"method": "POST"})

    summary = collector.get_summary()
    assert summary["counters"]["requests"]["method=GET"] == 1
    assert summary["counters"]["requests"]["method=POST"] == 2
    print("  ✅ 测试 1 通过：计数器")

    # 测试 2: 仪表
    collector.gauge("active_connections", 5.0, labels={"region": "us-east"})
    summary2 = collector.get_summary()
    assert summary2["gauges"]["active_connections"]["region=us-east"] == 5.0
    print("  ✅ 测试 2 通过：仪表")

    # 测试 3: 直方图 + 汇总
    for v in [0.1, 0.2, 0.3, 0.4, 0.5]:
        collector.record("latency", v, labels={"endpoint": "/api"})

    summary3 = collector.get_summary()
    hist = summary3["histograms"]["latency"]["endpoint=/api"]
    assert hist["count"] == 5
    assert hist["mean"] == 0.3
    assert hist["min"] == 0.1
    assert hist["max"] == 0.5
    assert hist["p50"] == 0.3
    print("  ✅ 测试 3 通过：直方图 + 汇总")

    # 测试 4: 事件自动采集
    collector2 = MetricsCollector()
    evt = CyberneticsEvent.create(
        EventType.TOOL_RESULT,
        "sess_001",
        {"tool_name": "search", "duration": 1.5, "success": True},
    )
    collector2.record_event(evt)

    summary4 = collector2.get_summary()
    assert summary4["counters"]["tool_calls_total"]["tool=search"] == 1
    assert summary4["histograms"]["tool_latency_seconds"]["tool=search"]["count"] == 1
    print("  ✅ 测试 4 通过：事件自动采集")

    # 测试 5: 成功率计算
    collector3 = MetricsCollector()
    for _ in range(8):
        collector3.record_event(CyberneticsEvent.create(
            EventType.TOOL_RESULT, "s1", {"tool_name": "t1"}
        ))
    for _ in range(2):
        collector3.record_event(CyberneticsEvent.create(
            EventType.TOOL_ERROR, "s1", {"tool_name": "t1"}
        ))
    summary5 = collector3.get_summary()
    assert abs(summary5["tool_success_rate"] - 0.8) < 0.01
    print("  ✅ 测试 5 通过：成功率计算")

    print("\n  ✅ 指标采集器所有冒烟测试通过！")
