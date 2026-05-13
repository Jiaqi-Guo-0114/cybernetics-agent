"""
告警系统核心模型。

定义告警事件、告警规则和告警等级的基础类。
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AlertEvent:
    """告警事件。"""
    rule_name: str
    severity: str = "warning"
    message: str = ""
    metric_name: str | None = None
    metric_value: float | None = None
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "rule_name": self.rule_name,
            "severity": self.severity,
            "message": self.message,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "labels": self.labels,
            "timestamp": self.timestamp,
        }


class AlertRule(ABC):
    """告警规则基类。"""
    name: str = ""
    severity: str = "warning"
    channels: list[str] = []

    @abstractmethod
    def evaluate(self, metrics: Any) -> AlertEvent | None:
        """
        评估是否触发告警。

        Args:
            metrics: MetricsCollector 或任何提供指标数据的对象。

        Returns:
            触发时返回 AlertEvent，否则返回 None。
        """
