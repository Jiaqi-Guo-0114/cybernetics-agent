"""
告警与通知系统。

提供多渠道告警能力，支持 stdout、飞书、Discord、钉钉、Slack、Email 等。
"""

from __future__ import annotations

from .core import AlertEvent, AlertRule

__all__ = ["AlertEvent", "AlertRule"]
