"""
PID 控制器实现。

基于钱学森工程控制论的经典比例-积分-微分控制器。

用于自动化参数调整场景，如：
- LLM temperature 自动调控
- 并发工具数量调控
- API 调用频率调控

使用示例：
    >>> pid = PIDController(kp=1.0, ki=0.1, kd=0.05, setpoint=0.8)
    >>> output = pid.update(measured_value=0.7, dt=1.0)
    >>> print(f"调整量: {output}")
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PIDState:
    """PID 控制器状态。"""
    setpoint: float = 0.0
    error_sum: float = 0.0
    last_error: float = 0.0
    last_time: float = field(default_factory=time.time)
    output_min: float = -float("inf")
    output_max: float = float("inf")


class PIDController:
    """
    PID 控制器。

    通过比例、积分、微分三项计算控制输出，
    使系统输出快速接近目标值。
    """

    def __init__(
        self,
        kp: float = 1.0,
        ki: float = 0.0,
        kd: float = 0.0,
        setpoint: float = 0.0,
        output_min: float = -float("inf"),
        output_max: float = float("inf"),
        integral_limit: float | None = None,
    ) -> None:
        """
        初始化 PID 控制器。

        参数:
            kp: 比例系数
            ki: 积分系数
            kd: 微分系数
            setpoint: 目标值
            output_min: 输出下限
            output_max: 输出上限
            integral_limit: 积分项累积限制（防止积分饱和）
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.state = PIDState(
            setpoint=setpoint,
            output_min=output_min,
            output_max=output_max,
        )
        self.integral_limit = integral_limit

    def update(self, measured_value: float, dt: float | None = None) -> float:
        """
        更新 PID 控制器，返回控制输出。

        参数:
            measured_value: 当前测量值
            dt: 时间间隔（秒）。为 None 时自动计算。

        返回:
            控制输出值
        """
        now = time.time()
        if dt is None:
            dt = now - self.state.last_time
        if dt <= 0:
            dt = 0.001  # 防止除零

        error = self.state.setpoint - measured_value

        # 积分项
        self.state.error_sum += error * dt
        if self.integral_limit is not None:
            self.state.error_sum = max(
                -self.integral_limit,
                min(self.integral_limit, self.state.error_sum),
            )

        # 微分项
        derivative = (error - self.state.last_error) / dt

        # PID 输出
        output = (
            self.kp * error +
            self.ki * self.state.error_sum +
            self.kd * derivative
        )

        # 限幅
        output = max(self.state.output_min, min(self.state.output_max, output))

        # 更新状态
        self.state.last_error = error
        self.state.last_time = now

        return output

    def reset(self) -> None:
        """重置控制器状态。"""
        self.state.error_sum = 0.0
        self.state.last_error = 0.0
        self.state.last_time = time.time()

    def set_setpoint(self, value: float) -> None:
        """设置新的目标值。"""
        self.state.setpoint = value

    def get_status(self) -> dict[str, Any]:
        """获取当前状态。"""
        return {
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd,
            "setpoint": self.state.setpoint,
            "last_error": self.state.last_error,
            "error_sum": self.state.error_sum,
            "output_limits": [self.state.output_min, self.state.output_max],
        }


class AutoTuningPID:
    """
    自动调参 PID 控制器。

    使用 Ziegler-Nichols 方法自动整定 PID 参数。
    """

    def __init__(self, setpoint: float = 0.0) -> None:
        self.setpoint = setpoint
        self._pid: PIDController | None = None
        self._oscillation_log: list[tuple[float, float]] = []
        self._tuned = False

    def record(self, measured_value: float, timestamp: float | None = None) -> None:
        """
        记录测量值用于自动调参。

        需要记录至少3个振荡周期的数据才能自动整定。
        """
        ts = timestamp or time.time()
        self._oscillation_log.append((ts, measured_value))

        # 保留最近3分钟的数据
        cutoff = ts - 180
        self._oscillation_log = [
            (t, v) for t, v in self._oscillation_log if t > cutoff
        ]

        if not self._tuned and len(self._oscillation_log) >= 10:
            self._auto_tune()

    def _auto_tune(self) -> None:
        """使用简化的 Ziegler-Nichols 方法调参。"""
        if len(self._oscillation_log) < 10:
            return

        # 计算振荡周期（简化版：检测极值点）
        values = [v for _, v in self._oscillation_log]
        peaks = []
        for i in range(1, len(values) - 1):
            if values[i] > values[i - 1] and values[i] > values[i + 1]:
                peaks.append((self._oscillation_log[i][0], values[i]))

        if len(peaks) < 2:
            return

        # 计算平均周期
        periods = [peaks[i][0] - peaks[i - 1][0] for i in range(1, len(peaks))]
        if not periods:
            return

        period = sum(periods) / len(periods)
        amplitude = sum(p[1] for p in peaks) / len(peaks)

        if period <= 0 or amplitude <= 0:
            return

        # Ziegler-Nichols 经验公式
        ku = 4.0 / (amplitude * 3.14159)  # 简化的临界增益
        tu = period

        kp = 0.6 * ku
        ki = kp / (0.5 * tu)
        kd = kp * 0.125 * tu

        self._pid = PIDController(
            kp=kp,
            ki=ki,
            kd=kd,
            setpoint=self.setpoint,
        )
        self._tuned = True

    def get_pid(self) -> PIDController | None:
        """获取调整后的 PID 控制器。"""
        return self._pid

    @property
    def is_tuned(self) -> bool:
        return self._tuned
