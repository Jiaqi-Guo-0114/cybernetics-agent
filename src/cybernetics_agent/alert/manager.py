"""
告警管理器。

统一管理规则、渠道、告警历史。
"""

from __future__ import annotations

import contextlib
from collections import deque
from typing import Any

from .channels.base import AlertChannel
from .core import AlertEvent, AlertRule


class AlertManager:
    """
    告警管理器。

    管理规则引擎、通知渠道和告警历史。
    """

    def __init__(self, history_size: int = 100, event_store: Any | None = None) -> None:
        self._rules: list[AlertRule] = []
        self._channels: dict[str, AlertChannel] = {}
        self._history: deque[AlertEvent] = deque(maxlen=history_size)
        self._event_store = event_store

    def add_rule(self, rule: AlertRule) -> None:
        """添加告警规则。"""
        self._rules.append(rule)

    def remove_rule(self, name: str) -> bool:
        """移除指定名称的规则。"""
        for i, r in enumerate(self._rules):
            if getattr(r, "name", "") == name:
                self._rules.pop(i)
                return True
        return False

    def register_channel(self, name: str, channel: AlertChannel) -> None:
        """注册通知渠道。"""
        self._channels[name] = channel

    def unregister_channel(self, name: str) -> bool:
        """注销通知渠道。"""
        return self._channels.pop(name, None) is not None

    def evaluate(self, metrics: Any) -> list[AlertEvent]:
        """
        评估所有规则。

        返回触发的告警事件列表。
        """
        triggered: list[AlertEvent] = []
        for rule in self._rules:
            if not hasattr(rule, "evaluate"):
                continue
            try:
                evt = rule.evaluate(metrics)
                if evt is not None:
                    triggered.append(evt)
                    self._history.append(evt)
                    if self._event_store is not None:
                        with contextlib.suppress(Exception):
                            self._event_store.write_alert(
                                rule_name=evt.rule_name,
                                severity=evt.severity,
                                message=evt.message,
                                metric_name=evt.metric_name,
                                metric_value=evt.metric_value,
                                labels=evt.labels,
                            )
            except Exception:
                continue
        return triggered

    def dispatch(self, event: AlertEvent, channel_names: list[str] | None = None) -> dict[str, bool]:
        """
        发送告警到指定渠道。

        如果未指定渠道，则发送到所有已注册渠道。
        """
        results: dict[str, bool] = {}
        targets = channel_names or list(self._channels.keys())
        for name in targets:
            ch = self._channels.get(name)
            if not ch:
                results[name] = False
                continue
            try:
                results[name] = ch.send(event)
            except Exception:
                results[name] = False
        return results

    def get_status(self) -> dict[str, Any]:
        """获取告警系统状态。"""
        return {
            "rules": [
                {
                    "name": getattr(r, "name", "unknown"),
                    "type": r.__class__.__name__,
                }
                for r in self._rules
            ],
            "channels": [
                {"name": name, "healthy": ch.health_check()}
                for name, ch in self._channels.items()
            ],
            "history": [evt.to_dict() for evt in self._history],
        }

    def clear_history(self) -> None:
        """清空告警历史。"""
        self._history.clear()
