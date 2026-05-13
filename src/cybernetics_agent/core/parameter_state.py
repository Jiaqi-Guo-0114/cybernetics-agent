"""
参数状态模型。

单个参数的学习状态数据类。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParameterState:
    """单个参数的学习状态。"""
    name: str
    current_value: Any
    base_value: Any
    min_value: Any = None
    max_value: Any = None
    options: list[Any] = field(default_factory=list)
    ema_value: float = 0.0
    adjustment_count: int = 0
