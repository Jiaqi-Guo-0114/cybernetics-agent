"""
告警渠道集合。

每个渠道单独实现，零依赖。
"""

from __future__ import annotations

from .base import AlertChannel
from .stdout import StdoutChannel

__all__ = ["AlertChannel", "StdoutChannel"]
