"""
控制论深度算法测试：PID + Bandit + MPC。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent.core.bandit import ThompsonSamplingBandit, UCBBandit
from cybernetics_agent.core.mpc_controller import MPCController, ResourceMPC
from cybernetics_agent.core.pid_controller import AutoTuningPID, PIDController


def test_pid_basic():
    """PID 控制器基本功能。"""
    pid = PIDController(kp=1.0, ki=0.1, kd=0.05, setpoint=10.0)
    output = pid.update(measured_value=5.0, dt=1.0)
    # 误差=5, 积分=5, 微分=5
    # output = 1.0*5 + 0.1*5 + 0.05*5 = 5.75
    assert output > 0
    assert pid.state.last_error == 5.0


def test_pid_reset():
    """PID 重置。"""
    pid = PIDController(kp=1.0, setpoint=10.0)
    pid.update(measured_value=5.0, dt=1.0)
    assert pid.state.error_sum != 0.0
    pid.reset()
    assert pid.state.error_sum == 0.0


def test_pid_limits():
    """PID 输出限幅。"""
    pid = PIDController(kp=100.0, setpoint=10.0, output_min=-5.0, output_max=5.0)
    output = pid.update(measured_value=0.0, dt=1.0)
    assert output <= 5.0
    assert output >= -5.0


def test_pid_integral_limit():
    """PID 积分限制。"""
    pid = PIDController(kp=0.0, ki=1.0, setpoint=10.0, integral_limit=5.0)
    for _ in range(100):
        pid.update(measured_value=0.0, dt=1.0)
    assert abs(pid.state.error_sum) <= 5.0


def test_pid_setpoint_change():
    """PID 设置新目标值。"""
    pid = PIDController(setpoint=10.0)
    assert pid.state.setpoint == 10.0
    pid.set_setpoint(20.0)
    assert pid.state.setpoint == 20.0


def test_pid_status():
    """PID 状态查询。"""
    pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
    status = pid.get_status()
    assert status["kp"] == 1.0
    assert "error_sum" in status


def test_autotuning_pid():
    """自动调参 PID。"""
    import math
    at = AutoTuningPID(setpoint=0.8)
    assert not at.is_tuned

    # 模拟振荡数据
    for i in range(20):
        t = i * 0.5
        v = 0.8 + 0.1 * math.sin(t * 2)
        at.record(v, timestamp=t)

    pid = at.get_pid()
    if pid is not None:
        assert at.is_tuned
        assert pid.kp > 0


def test_ucb_bandit():
    """UCB1 算法。"""
    bandit = UCBBandit(arms=["a", "b", "c"])

    # 第一轮：每个手臂都应该被拉一次
    for _ in range(3):
        arm = bandit.select()
        bandit.update(arm, reward=0.5)

    assert bandit.total_pulls == 3

    # 后续：更多拉取
    for _ in range(100):
        arm = bandit.select()
        # 假设 b 表现最好
        reward = 0.9 if arm == "b" else 0.3
        bandit.update(arm, reward=reward)

    # b 应该被拉最多次
    status = bandit.get_status()
    b_pulls = next(s["pulls"] for s in status["arms"] if s["name"] == "b")
    assert b_pulls > 30  # 大部分拉取应该是 b


def test_thompson_sampling():
    """Thompson Sampling 算法。"""
    bandit = ThompsonSamplingBandit(arms=["x", "y"])

    # 模拟 y 更容易成功
    for _ in range(100):
        arm = bandit.select()
        success = arm == "y"
        bandit.update(arm, success=success)

    status = bandit.get_status()
    y_stats = next(s for s in status["arms"] if s["name"] == "y")
    assert y_stats["expected"] > 0.5


def test_thompson_continuous_reward():
    """Thompson Sampling 连续收益。"""
    bandit = ThompsonSamplingBandit(arms=["x", "y"])
    bandit.update_reward("x", reward=0.2)
    bandit.update_reward("y", reward=0.8)
    status = bandit.get_status()
    y_stats = next(s for s in status["arms"] if s["name"] == "y")
    assert y_stats["expected"] > 0.5


def test_mpc_basic():
    """MPC 基本功能。"""
    mpc = MPCController(
        horizon=3,
        model_gain=1.0,
        control_min=-10.0,
        control_max=10.0,
    )
    control = mpc.optimize(current_state=50.0, target=80.0)
    assert control >= -10.0
    assert control <= 10.0


def test_mpc_predict():
    """MPC 预测轨迹。"""
    mpc = MPCController(horizon=3, model_gain=2.0)
    trajectory = mpc.predict(initial_state=0.0, control_sequence=[1.0, 1.0, 1.0])
    assert len(trajectory) == 4
    assert trajectory[-1] == 6.0  # 0 + 2*1 + 2*1 + 2*1 = 6


def test_mpc_cost():
    """MPC 成本函数。"""
    mpc = MPCController(state_cost=1.0, control_cost=0.1)
    mpc.state.target = 10.0
    trajectory = [0.0, 5.0, 8.0, 10.0]
    controls = [5.0, 3.0, 2.0]
    cost = mpc.cost(trajectory, controls)
    assert cost > 0


def test_mpc_constraint():
    """MPC 约束。"""
    mpc = MPCController(control_min=0.0, control_max=100.0)
    # 添加约束：控制量不能超过状态的 2 倍
    mpc.add_constraint(lambda u, x: u <= 2 * x)
    control = mpc.optimize(current_state=10.0, target=50.0)
    assert control <= 20.0  # 受限于约束


def test_resource_mpc():
    """ResourceMPC 资源分配。"""
    rpc = ResourceMPC(resource_limit=100.0, target_utilization=0.8)
    allocation = rpc.allocate(current_utilization=50.0)
    assert allocation >= 0.0
    assert allocation <= 100.0

    status = rpc.get_status()
    assert status["resource_limit"] == 100.0
    assert status["target_utilization"] == 0.8
