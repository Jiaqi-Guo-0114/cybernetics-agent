"""
告警规则引擎。

支持阈值规则、频率限制、静默期。
"""

from __future__ import annotations

import time
from typing import Any

from .core import AlertEvent, AlertRule


class ThresholdRule(AlertRule):
    """
    阈值规则。

    当指标持续超过阈值指定时间后触发告警。
    """

    def __init__(
        self,
        name: str,
        metric: str,
        operator: str,
        threshold: float,
        duration: float = 0.0,
        severity: str = "warning",
        channels: list[str] | None = None,
    ) -> None:
        self.name = name
        self.metric = metric
        self.operator = operator
        self.threshold = threshold
        self.duration = duration
        self.severity = severity
        self.channels = channels or []

        self._first_trigger_time: float | None = None
        self._last_trigger_time: float | None = None

    def evaluate(self, metrics: Any) -> AlertEvent | None:
        """评估是否触发告警。"""
        value = self._get_metric_value(metrics)
        if value is None:
            return None

        triggered = self._compare(value)
        now = time.time()

        if not triggered:
            self._first_trigger_time = None
            return None

        if self._first_trigger_time is None:
            self._first_trigger_time = now
            if self.duration <= 0:
                self._last_trigger_time = now
                return self._create_event(value, 0.0)
            return None

        elapsed = now - self._first_trigger_time
        if elapsed >= self.duration:
            self._last_trigger_time = now
            return self._create_event(value, elapsed)

        return None

    def _create_event(self, value: float, elapsed: float) -> AlertEvent:
        """创建告警事件。"""
        return AlertEvent(
            rule_name=self.name,
            severity=self.severity,
            message=(
                f"{self.metric} {self.operator} {self.threshold} "
                f"(当前值: {value:.4f}, 持续 {elapsed:.1f}秒)"
            ),
            metric_name=self.metric,
            metric_value=value,
            labels={"operator": self.operator, "threshold": str(self.threshold)},
        )

    def _get_metric_value(self, metrics: Any) -> float | None:
        """从 metrics 中获取指标值。"""
        if hasattr(metrics, "get_metric"):
            return metrics.get_metric(self.metric)
        if isinstance(metrics, dict):
            return metrics.get(self.metric)
        return None

    def _compare(self, value: float) -> bool:
        """比较值与阈值。"""
        ops = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }
        op = ops.get(self.operator)
        if not op:
            return False
        return op(value, self.threshold)


class RateRule:
    """
    频率限制规则。

    限制单位时间内的告警数量。
    """

    def __init__(self, max_alerts: int, window: float) -> None:
        self.max_alerts = max_alerts
        self.window = window
        self._alerts: list[float] = []

    def allow(self) -> bool:
        """检查是否允许发送告警。"""
        now = time.time()
        cutoff = now - self.window
        self._alerts = [t for t in self._alerts if t > cutoff]
        if len(self._alerts) < self.max_alerts:
            self._alerts.append(now)
            return True
        return False


class SilenceRule:
    """
    静默期规则。

    告警触发后，在指定时间内不再触发。
    """

    def __init__(self, duration: float) -> None:
        self.duration = duration
        self._last_alert_time: float | None = None

    def allow(self) -> bool:
        """检查是否已过静默期。"""
        if self._last_alert_time is None:
            return True
        return (time.time() - self._last_alert_time) >= self.duration

    def record_alert(self) -> None:
        """记录告警触发时间。"""
        self._last_alert_time = time.time()
