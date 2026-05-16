"""
告警聚合与抑制。

按 group_by 字段聚合告警，在指定时间窗口内抑制重复告警。

支持的聚合策略：
- first: 窗口内只保留第一个告警
- last: 窗口内只保留最后一个告警
- count: 窗口结束时发送聚合统计（X条告警被聚合）

使用示例：
    >>> aggregator = AlertAggregator(
    ...     group_by=["rule_name", "severity"],
    ...     window_seconds=300,
    ...     strategy="count",
    ... )
    >>> event = aggregator.process(alert_event)
    >>> if event:
    ...     # 发送 event
    ...     pass
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from .core import AlertEvent


@dataclass
class _AlertGroup:
    """内部：告警组状态。"""
    first_event: AlertEvent
    last_event: AlertEvent
    count: int = 1
    window_start: float = field(default_factory=time.time)


class AlertAggregator:
    """
    告警聚合器。

    将符合 group_by 条件的告警聚合在一起，减少噪声通知。
    """

    def __init__(
        self,
        group_by: list[str] | None = None,
        window_seconds: float = 300.0,
        strategy: str = "count",
        max_groups: int = 1000,
    ) -> None:
        """
        初始化聚合器。

        参数:
            group_by: 聚合键列表。支持 "rule_name"、"severity"、"metric_name"、
                     以及 labels 中的任意字段（用 "labels.key" 表示）。
                     默认 ["rule_name", "severity"]。
            window_seconds: 聚合时间窗口（秒）。默认 300。
            strategy: 聚合策略。"first" | "last" | "count"。默认 "count"。
            max_groups: 最大组数量。超过时清除最早的组。
        """
        self.group_by = group_by or ["rule_name", "severity"]
        self.window_seconds = window_seconds
        self.strategy = strategy
        self.max_groups = max_groups
        self._groups: dict[str, _AlertGroup] = {}

    def process(self, event: AlertEvent) -> AlertEvent | None:
        """
        处理单个告警事件。

        如果事件被抑制，返回 None。
        如果窗口已过期或第一次见到该组，返回告警事件。
        如果策略为 count 且窗口未过期，返回 None（等窗口结束时再发送）。

        参数:
            event: 告警事件

        返回:
            需要发送的告警事件，或 None（被抑制）。
        """
        now = time.time()
        group_key = self._make_key(event)

        existing = self._groups.get(group_key)

        if existing is None:
            # 新组：创建新窗口
            self._groups[group_key] = _AlertGroup(
                first_event=event,
                last_event=event,
                count=1,
                window_start=now,
            )
            # 清理过期组和超出限制的组
            self._cleanup_expired(now)
            if self.strategy == "count":
                # count 策略下，第一个告警也不立即发送，等窗口结束
                return None
            return event

        # 检查窗口是否过期
        elapsed = now - existing.window_start
        if elapsed >= self.window_seconds:
            # 窗口过期：返回上一个窗口的聚合结果
            result = self._make_aggregated_event(existing)
            # 用当前事件创建新窗口
            self._groups[group_key] = _AlertGroup(
                first_event=event,
                last_event=event,
                count=1,
                window_start=now,
            )
            self._cleanup_expired(now)
            if self.strategy == "count":
                # count 策略下，新窗口的第一个告警也不立即发送
                return result  # 返回上一个窗口的聚合结果
            return result

        # 窗口未过期：更新组并抑制
        existing.last_event = event
        existing.count += 1
        self._cleanup_expired(now)
        return None

    def flush(self) -> list[AlertEvent]:
        """
        强制刷新所有组，返回所有待发送的聚合告警。

        无论窗口是否过期，都会被刷新。
        """
        results: list[AlertEvent] = []
        keys = list(self._groups.keys())
        for key in keys:
            group = self._groups.pop(key)
            results.append(self._make_aggregated_event(group))
        return results

    def _make_key(self, event: AlertEvent) -> str:
        """根据 group_by 字段生成组键。"""
        parts: list[str] = []
        for field in self.group_by:
            if field == "rule_name":
                parts.append(f"rule={event.rule_name}")
            elif field == "severity":
                parts.append(f"sev={event.severity}")
            elif field == "metric_name":
                parts.append(f"metric={event.metric_name or ''}")
            elif field.startswith("labels."):
                label_key = field[7:]
                parts.append(f"l_{label_key}={event.labels.get(label_key, '')}")
            else:
                parts.append(f"{field}={getattr(event, field, '')}")
        return "|".join(parts)

    def _make_aggregated_event(self, group: _AlertGroup) -> AlertEvent:
        """根据策略生成聚合后的告警事件。"""
        if self.strategy == "first":
            return group.first_event

        if self.strategy == "last":
            return group.last_event

        # count 策略：发送聚合统计
        event = group.first_event
        return AlertEvent(
            rule_name=event.rule_name,
            severity=event.severity,
            message=(
                f"[聚合] {group.count} 条告警被聚合 | "
                f"最新: {group.last_event.message}"
            ),
            metric_name=event.metric_name,
            metric_value=group.last_event.metric_value,
            labels={
                **event.labels,
                "_aggregated_count": str(group.count),
                "_aggregated_strategy": self.strategy,
            },
            timestamp=time.time(),
        )

    def _cleanup_expired(self, now: float) -> None:
        """清理过期组，确保不超过 max_groups。"""
        expired = [
            k for k, g in self._groups.items()
            if (now - g.window_start) >= self.window_seconds * 2
        ]
        for k in expired:
            del self._groups[k]

        # 如果仍然超过最大组数，删除最早的
        while len(self._groups) > self.max_groups:
            oldest = min(self._groups, key=lambda k: self._groups[k].window_start)
            del self._groups[oldest]

    def get_stats(self) -> dict[str, Any]:
        """获取聚合器统计信息。"""
        now = time.time()
        return {
            "group_by": self.group_by,
            "window_seconds": self.window_seconds,
            "strategy": self.strategy,
            "active_groups": len(self._groups),
            "groups": {
                k: {
                    "count": g.count,
                    "window_age": round(now - g.window_start, 1),
                }
                for k, g in self._groups.items()
            },
        }
