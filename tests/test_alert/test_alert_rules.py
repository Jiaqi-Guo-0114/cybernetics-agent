"""
告警规则引擎测试。
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.alert.rules import RateRule, SilenceRule, ThresholdRule


def test_threshold_rule_trigger():
    """阈值规则正确触发。"""
    rule = ThresholdRule(
        name="high_error",
        metric="error_rate",
        operator=">",
        threshold=0.3,
        duration=0,  # 无延迟
    )
    evt = rule.evaluate({"error_rate": 0.5})
    assert evt is not None
    assert evt.rule_name == "high_error"
    assert evt.metric_value == 0.5


def test_threshold_rule_no_trigger():
    """阈值规则不应触发。"""
    rule = ThresholdRule(
        name="high_error",
        metric="error_rate",
        operator=">",
        threshold=0.3,
    )
    evt = rule.evaluate({"error_rate": 0.1})
    assert evt is None


def test_threshold_rule_with_duration():
    """带持续时间的阈值规则。"""
    rule = ThresholdRule(
        name="high_error",
        metric="error_rate",
        operator=">",
        threshold=0.3,
        duration=0.5,
    )
    # 第一次触发，未达持续时间
    evt = rule.evaluate({"error_rate": 0.5})
    assert evt is None

    # 等待超过持续时间
    time.sleep(0.6)
    evt = rule.evaluate({"error_rate": 0.5})
    assert evt is not None
    assert "持续" in evt.message


def test_threshold_rule_all_operators():
    """所有比较操作符正确工作。"""
    for op, value, expected in [
        (">", 0.5, True),
        ("<", 0.1, True),
        (">=", 0.3, True),
        ("<=", 0.3, True),
        ("==", 0.3, True),
        ("!=", 0.5, True),
    ]:
        rule = ThresholdRule(name="t", metric="m", operator=op, threshold=0.3, duration=0)
        evt = rule.evaluate({"m": value})
        assert (evt is not None) == expected, f"operator {op} failed with value {value}"


def test_rate_rule():
    """频率限制规则。"""
    rule = RateRule(max_alerts=2, window=1.0)
    assert rule.allow() is True
    assert rule.allow() is True
    assert rule.allow() is False  # 超过限制

    # 等待窗口过期
    time.sleep(1.1)
    assert rule.allow() is True


def test_silence_rule():
    """静默期规则。"""
    rule = SilenceRule(duration=0.5)
    assert rule.allow() is True

    rule.record_alert()
    assert rule.allow() is False  # 静默期内

    time.sleep(0.6)
    assert rule.allow() is True  # 静默期过了
