"""
标准输出渠道。

默认启用，零依赖，用于本地调试和开发。
"""

from __future__ import annotations

import sys
from typing import Any

from ..core import AlertEvent
from .base import AlertChannel


class StdoutChannel(AlertChannel):
    """输出告警到标准输出。"""
    name = "stdout"

    def __init__(self, stream: Any = None) -> None:
        self._stream = stream or sys.stdout

    def send(self, event: AlertEvent) -> bool:
        """输出告警事件。"""
        line = (
            f"[告警:{event.severity.upper()}] {event.rule_name} | "
            f"{event.message}"
        )
        if event.metric_name:
            line += f" | {event.metric_name}={event.metric_value}"
        self._stream.write(line + "\n")
        return True
