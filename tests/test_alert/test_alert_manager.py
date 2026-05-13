"""
AlertManager 测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.alert import (
    AlertEvent,
    AlertManager,
    ThresholdRule,
)
from cybernetics_agent.alert.channels import StdoutChannel


def test_manager_add_rule():
    """添加规则正确。"""
    mgr = AlertManager()
    rule = ThresholdRule(name="r1", metric="m1", operator=">", threshold=1.0, duration=0)
    mgr.add_rule(rule)
    status = mgr.get_status()
    assert len(status["rules"]) == 1
    assert status["rules"][0]["name"] == "r1"


def test_manager_register_channel():
    """注册渠道正确。"""
    mgr = AlertManager()
    mgr.register_channel("stdout", StdoutChannel())
    status = mgr.get_status()
    assert len(status["channels"]) == 1
    assert status["channels"][0]["name"] == "stdout"


def test_manager_evaluate():
    """评估规则正确触发。"""
    mgr = AlertManager()
    rule = ThresholdRule(name="r1", metric="m1", operator=">", threshold=1.0, duration=0)
    mgr.add_rule(rule)
    evts = mgr.evaluate({"m1": 2.0})
    assert len(evts) == 1
    assert evts[0].rule_name == "r1"


def test_manager_history():
    """历史记录正确。"""
    mgr = AlertManager(history_size=3)
    for i in range(5):
        rule = ThresholdRule(name=f"r{i}", metric="m", operator=">", threshold=0, duration=0)
        mgr.add_rule(rule)
    mgr.evaluate({"m": 1.0})
    status = mgr.get_status()
    assert len(status["history"]) == 3  # 最多保留 3 条


def test_manager_dispatch():
    """分发告警正确。"""
    import io
    stream = io.StringIO()
    mgr = AlertManager()
    mgr.register_channel("stdout", StdoutChannel(stream=stream))
    evt = AlertEvent(rule_name="r1", severity="error", message="test")
    results = mgr.dispatch(evt)
    assert results["stdout"] is True
    assert "告警:ERROR" in stream.getvalue()


def test_manager_remove_rule():
    """移除规则正确。"""
    mgr = AlertManager()
    rule = ThresholdRule(name="r1", metric="m", operator=">", threshold=1.0, duration=0)
    mgr.add_rule(rule)
    assert mgr.remove_rule("r1") is True
    assert mgr.remove_rule("r1") is False


def test_manager_clear_history():
    """清空历史正确。"""
    mgr = AlertManager()
    rule = ThresholdRule(name="r1", metric="m", operator=">", threshold=0, duration=0)
    mgr.add_rule(rule)
    mgr.evaluate({"m": 1.0})
    mgr.clear_history()
    assert len(mgr.get_status()["history"]) == 0
