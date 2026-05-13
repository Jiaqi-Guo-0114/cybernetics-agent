"""
告警渠道基类。

所有通知渠道（stdout、飞书、Discord 等）均继承此基类。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core import AlertEvent


class AlertChannel(ABC):
    """告警渠道抽象基类。"""
    name: str = ""

    @abstractmethod
    def send(self, event: AlertEvent) -> bool:
        """
        发送告警事件。

        Args:
            event: 告警事件。

        Returns:
            发送成功返回 True，否则返回 False。
        """

    def health_check(self) -> bool:
        """
        健康检查。

        默认返回 True。子类可重写以检查渠道可用性。
        """
        return True
