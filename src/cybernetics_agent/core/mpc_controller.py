"""
模型预测控制（MPC）实现。

通过预测未来的状态轨迹，优化控制序列使得目标函数最小化。

应用场景：
- API 调用频率限制（在不触发限制的前提下最大化请求量）
- 并发工具数量控制
- 成本优化

使用示例：
    >>> mpc = MPCController(horizon=5, model_gain=0.8)
    >>> control = mpc.optimize(current_state=50, target=80)
    >>> print(f"控制量: {control}")
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class MPCState:
    """MPC 控制器状态。"""
    current: float = 0.0
    target: float = 0.0
    last_control: float = 0.0
    last_time: float = field(default_factory=time.time)


class MPCController:
    """
    简化的 MPC 控制器。

    基于线性模型：x_{t+1} = x_t + gain * u_t * dt

    优化目标：
        J = sum(state_cost * (target - x_t)^2 + control_cost * u_t^2)
    """

    def __init__(
        self,
        horizon: int = 5,
        model_gain: float = 1.0,
        dt: float = 1.0,
        control_min: float = -float("inf"),
        control_max: float = float("inf"),
        state_cost: float = 1.0,
        control_cost: float = 0.1,
    ) -> None:
        """
        初始化 MPC 控制器。

        参数:
            horizon: 预测时域
            model_gain: 模型增益
            dt: 时间步长
            control_min: 控制量下限
            control_max: 控制量上限
            state_cost: 状态偏差惩罚系数
            control_cost: 控制量惩罚系数
        """
        self.horizon = horizon
        self.model_gain = model_gain
        self.dt = dt
        self.control_min = control_min
        self.control_max = control_max
        self.state_cost = state_cost
        self.control_cost = control_cost
        self.state = MPCState()
        self._constraints: list[Callable[[float, float], bool]] = []

    def add_constraint(self, fn: Callable[[float, float], bool]) -> None:
        """
        添加约束函数。

        约束函数签名: fn(control, state) -> bool
        """
        self._constraints.append(fn)

    def predict(self, initial_state: float, control_sequence: list[float]) -> list[float]:
        """
        预测状态轨迹。

        参数:
            initial_state: 初始状态
            control_sequence: 控制序列

        返回:
            状态轨迹列表
        """
        trajectory = [initial_state]
        state = initial_state
        for u in control_sequence:
            state += self.model_gain * u * self.dt
            trajectory.append(state)
        return trajectory

    def cost(self, trajectory: list[float], control_sequence: list[float]) -> float:
        """
        计算目标函数值。

        参数:
            trajectory: 状态轨迹
            control_sequence: 控制序列

        返回:
            总成本
        """
        total = 0.0
        for i, u in enumerate(control_sequence):
            x = trajectory[i + 1]
            # 状态偏差成本
            total += self.state_cost * (self.state.target - x) ** 2
            # 控制量惩罚（防止过大的控制量）
            total += self.control_cost * u ** 2
        return total

    def optimize(self, current_state: float, target: float) -> float:
        """
        优化控制量。

        使用简化的线性搜索：在合理范围内尝试多个控制量，
        选择使成本函数最小的。

        参数:
            current_state: 当前状态
            target: 目标状态

        返回:
            最优控制量
        """
        self.state.current = current_state
        self.state.target = target

        # 离散化搜索空间
        best_cost = float("inf")
        best_control = 0.0

        # 在合理范围内采样200个点
        n_samples = 200
        step = (self.control_max - self.control_min) / n_samples

        for i in range(n_samples + 1):
            u = self.control_min + i * step
            sequence = [u] * self.horizon

            # 检查约束
            valid = True
            temp_state = current_state
            for ctrl in sequence:
                if not all(fn(ctrl, temp_state) for fn in self._constraints):
                    valid = False
                    break
                temp_state += self.model_gain * ctrl * self.dt

            if not valid:
                continue

            trajectory = self.predict(current_state, sequence)
            c = self.cost(trajectory, sequence)

            if c < best_cost:
                best_cost = c
                best_control = u

        self.state.last_control = best_control
        self.state.last_time = time.time()
        return best_control

    def get_status(self) -> dict[str, Any]:
        """获取当前状态。"""
        return {
            "current_state": self.state.current,
            "target": self.state.target,
            "last_control": self.state.last_control,
            "horizon": self.horizon,
            "model_gain": self.model_gain,
            "dt": self.dt,
            "state_cost": self.state_cost,
            "control_cost": self.control_cost,
            "constraints": len(self._constraints),
        }


class ResourceMPC:
    """
    资源分配 MPC。

    专门用于 API 调用频率、并发数等资源分配场景。
    """

    def __init__(
        self,
        resource_limit: float = 100.0,
        target_utilization: float = 0.8,
    ) -> None:
        """
        初始化资源分配 MPC。

        参数:
            resource_limit: 资源上限
            target_utilization: 目标利用率（0~1）
        """
        self.resource_limit = resource_limit
        self.target_utilization = target_utilization
        self.mpc = MPCController(
            horizon=3,
            model_gain=1.0,
            control_min=0.0,
            control_max=resource_limit,
            control_cost=0.001,
            state_cost=2.0,
        )

    def allocate(self, current_utilization: float) -> float:
        """
        计算下一步的资源分配。

        参数:
            current_utilization: 当前资源利用量

        返回:
            建议的资源分配量
        """
        target = self.resource_limit * self.target_utilization
        return self.mpc.optimize(
            current_state=current_utilization,
            target=target,
        )

    def get_status(self) -> dict[str, Any]:
        """获取当前状态。"""
        return {
            **self.mpc.get_status(),
            "resource_limit": self.resource_limit,
            "target_utilization": self.target_utilization,
        }
