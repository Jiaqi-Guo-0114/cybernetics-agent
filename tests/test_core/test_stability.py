"""
稳定性引擎模块的 pytest 测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core import CircuitBreaker, RetryPolicy, StabilityEngine


@pytest.fixture
def stability_engine():
    config = {
        "enabled": True,
        "timeout": {"default": 5.0},
        "retry": {"max_retries": 2, "backoff": "exponential", "base_delay": 0.1},
        "circuit_breaker": {"enabled": True, "failure_threshold": 3},
        "graceful_degradation": {"enabled": True},
    }
    ctx = CyberneticsContext(CyberneticsConfig())
    return StabilityEngine(config, ctx)


def test_retry_policy():
    policy = RetryPolicy(max_retries=3, backoff="exponential", base_delay=1.0)
    assert policy.get_delay(0) == 1.0
    assert policy.get_delay(1) == 2.0
    assert policy.get_delay(2) == 4.0


def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
    assert cb.can_execute() is True
    cb.record_failure()
    cb.record_failure()
    assert cb.get_status()["state"] == "open"
    assert cb.can_execute() is False


def test_retry_mechanism(stability_engine):
    attempt_count = [0]

    def flaky_func():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise RuntimeError("暂时错误")
        return "success"

    result = stability_engine.with_retry(flaky_func)
    assert result == "success"
    assert attempt_count[0] == 3


def test_permanent_error_no_retry(stability_engine):
    def permanent_error():
        raise RuntimeError("404 not found")

    with pytest.raises(RuntimeError, match="404"):
        stability_engine.with_retry(permanent_error)


def test_graceful_degradation(stability_engine):
    def primary():
        raise RuntimeError("主函数失败")

    def fallback():
        return "fallback_result"

    result = stability_engine.degrade(primary, [fallback])
    assert result == "fallback_result"
    assert stability_engine._degradation_count == 1
