"""AlertManager 剩余代码补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.alert.manager import AlertManager
from cybernetics_agent.alert.rules import ThresholdRule

class TestAlertManagerCoverage:
    def test_add_rule(self):
        mgr = AlertManager()
        rule = ThresholdRule("r", "cpu", ">", 80, 0)
        mgr.add_rule(rule)
        assert len(mgr.get_status().get("rules", [])) == 1

    def test_remove_rule(self):
        mgr = AlertManager()
        rule = ThresholdRule("r", "cpu", ">", 80, 0)
        mgr.add_rule(rule)
        mgr.remove_rule("r")
        assert len(mgr.get_status().get("rules", [])) == 0

    def test_evaluate_no_rules(self):
        mgr = AlertManager()
        alerts = mgr.evaluate({"cpu": 100})
        assert alerts == []

    def test_evaluate_triggered(self):
        mgr = AlertManager()
        mgr.add_rule(ThresholdRule("r", "cpu", ">", 0, 0))
        alerts = mgr.evaluate({"cpu": 100})
        assert len(alerts) >= 1

    def test_get_status(self):
        mgr = AlertManager()
        status = mgr.get_status()
        assert isinstance(status, dict)

    def test_clear_history(self):
        mgr = AlertManager()
        mgr.clear_history()

    def test_register_unregister_channel(self):
        mgr = AlertManager()
        from cybernetics_agent.alert.channels.stdout import StdoutChannel
        ch = StdoutChannel()
        mgr.register_channel("stdout", ch)
        mgr.unregister_channel("stdout")
