"""
告警核心模型测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.alert.core import AlertEvent


def test_alert_event_creation():
    """AlertEvent 能正确创建。"""
    evt = AlertEvent(
        rule_name="test_rule",
        severity="warning",
        message="测试告警",
        metric_name="error_rate",
        metric_value=0.5,
    )
    assert evt.rule_name == "test_rule"
    assert evt.severity == "warning"
    assert evt.message == "测试告警"
    assert evt.metric_name == "error_rate"
    assert evt.metric_value == 0.5


def test_alert_event_to_dict():
    """AlertEvent 能正确转换为字典。"""
    evt = AlertEvent(rule_name="r1", message="m1")
    d = evt.to_dict()
    assert d["rule_name"] == "r1"
    assert d["message"] == "m1"
    assert "timestamp" in d
