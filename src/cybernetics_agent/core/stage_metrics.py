"""
阶段指标模型。

单个阶段的性能指标数据类，用于转化漏斗和系统辨识。
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field


@dataclass
class StageMetrics:
    """单个阶段的性能指标。"""
    stage_name: str
    entry_count: int = 0
    exit_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    durations: list[float] = field(default_factory=list)

    @property
    def conversion_rate(self) -> float:
        if self.entry_count > 0:
            return self.exit_count / self.entry_count
        return 0.0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.error_count
        if total > 0:
            return self.success_count / total
        return 1.0

    @property
    def avg_duration(self) -> float:
        if self.durations:
            return statistics.mean(self.durations)
        return 0.0

    @property
    def p95_duration(self) -> float:
        if len(self.durations) >= 2:
            sorted_d = sorted(self.durations)
            idx = int(len(sorted_d) * 0.95)
            return sorted_d[min(idx, len(sorted_d) - 1)]
        return self.avg_duration
