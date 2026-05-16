"""
多臂老虎机算法。

支持 UCB1 和 Thompson Sampling 两种经典算法，
用于探索/利用均衡（exploration/exploitation）场景。

应用场景：
- LLM 模型选择（哪个模型在某个任务上表现最好？）
- 工具调用策略选择
- A/B 测试优化

使用示例：
    >>> bandit = UCBBandit(arms=["gpt-4", "claude-3", "kimi"])
    >>> arm = bandit.select()
    >>> bandit.update(arm, reward=0.9)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class ArmStats:
    """单个手臂的统计信息。"""
    name: str
    pulls: int = 0
    rewards: float = 0.0

    @property
    def mean(self) -> float:
        if self.pulls == 0:
            return 0.0
        return self.rewards / self.pulls


class UCBBandit:
    """
    UCB1 算法实现。

    Upper Confidence Bound 算法，通过给予未充分探索的手臂更高的信任上界，
    自动平衡探索与利用。

    公式: argmax(平均收益 + sqrt(2 * ln(总次数) / 该手臂次数))
    """

    def __init__(self, arms: list[str], c: float = math.sqrt(2)) -> None:
        """
        初始化 UCB1 老虎机。

        参数:
            arms: 手臂名称列表
            c: 探索参数，默认 sqrt(2)
        """
        self.arms = arms
        self.c = c
        self.stats: dict[str, ArmStats] = {
            arm: ArmStats(name=arm) for arm in arms
        }
        self.total_pulls = 0

    def select(self) -> str:
        """选择下一个手臂。"""
        # 首先确保每个手臂至少被拉一次
        for arm in self.arms:
            if self.stats[arm].pulls == 0:
                return arm

        # UCB 公式
        best_arm = self.arms[0]
        best_score = -float("inf")

        for arm in self.arms:
            stat = self.stats[arm]
            exploitation = stat.mean
            exploration = self.c * math.sqrt(
                math.log(self.total_pulls) / stat.pulls
            )
            score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_arm = arm

        return best_arm

    def update(self, arm: str, reward: float) -> None:
        """
        更新手臂的统计信息。

        参数:
            arm: 被选择的手臂名称
            reward: 收益值（0~1）
        """
        if arm not in self.stats:
            raise ValueError(f"Unknown arm: {arm}")
        self.stats[arm].pulls += 1
        self.stats[arm].rewards += reward
        self.total_pulls += 1

    def get_status(self) -> dict[str, Any]:
        """获取当前状态。"""
        return {
            "algorithm": "UCB1",
            "arms": [
                {
                    "name": s.name,
                    "pulls": s.pulls,
                    "mean_reward": round(s.mean, 4),
                }
                for s in self.stats.values()
            ],
            "total_pulls": self.total_pulls,
            "c": self.c,
        }


class ThompsonSamplingBandit:
    """
    Thompson Sampling 算法实现。

    使用 Beta 分布对每个手臂的成功概率进行建模，
    每次从后验分布中采样得到预测值，选择最高的手臂。

    适合二元收益场景（成功/失败）。
    """

    def __init__(self, arms: list[str]) -> None:
        """
        初始化 Thompson Sampling 老虎机。

        参数:
            arms: 手臂名称列表
        """
        self.arms = arms
        # Beta(α, β) 参数，α=成功次数+1，β=失败次数+1
        self.alpha: dict[str, float] = {arm: 1.0 for arm in arms}
        self.beta: dict[str, float] = {arm: 1.0 for arm in arms}
        self.total_pulls = 0

    def select(self) -> str:
        """从 Beta 分布中采样并选择最高值的手臂。"""
        samples = {
            arm: random.betavariate(self.alpha[arm], self.beta[arm])
            for arm in self.arms
        }
        return max(samples, key=samples.get)  # type: ignore[arg-type]

    def update(self, arm: str, success: bool) -> None:
        """
        更新 Beta 分布参数。

        参数:
            arm: 被选择的手臂
            success: 是否成功
        """
        if arm not in self.alpha:
            raise ValueError(f"Unknown arm: {arm}")
        if success:
            self.alpha[arm] += 1.0
        else:
            self.beta[arm] += 1.0
        self.total_pulls += 1

    def update_reward(self, arm: str, reward: float) -> None:
        """
        使用连续收益更新（将收益视为成功概率）。

        参数:
            arm: 被选择的手臂
            reward: 收益值（0~1）
        """
        if arm not in self.alpha:
            raise ValueError(f"Unknown arm: {arm}")
        # 将连续收益映射为 Beta 更新
        self.alpha[arm] += reward
        self.beta[arm] += (1.0 - reward)
        self.total_pulls += 1

    def get_status(self) -> dict[str, Any]:
        """获取当前状态。"""
        return {
            "algorithm": "ThompsonSampling",
            "arms": [
                {
                    "name": arm,
                    "alpha": round(self.alpha[arm], 2),
                    "beta": round(self.beta[arm], 2),
                    "expected": round(
                        self.alpha[arm] / (self.alpha[arm] + self.beta[arm]), 4
                    ),
                }
                for arm in self.arms
            ],
            "total_pulls": self.total_pulls,
        }
