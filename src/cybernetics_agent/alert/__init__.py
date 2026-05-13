"""
告警与通知系统。

提供多渠道告警能力，支持 stdout、飞书、Discord、钉钉、Slack、Email 等。
"""

from __future__ import annotations

from .core import AlertEvent, AlertRule
from .manager import AlertManager
from .rules import RateRule, SilenceRule, ThresholdRule

__all__ = [
    "AlertEvent",
    "AlertRule",
    "AlertManager",
    "ThresholdRule",
    "RateRule",
    "SilenceRule",
]
