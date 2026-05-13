"""Alert 最终补充"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.alert.manager import AlertManager
from cybernetics_agent.alert.rules import ThresholdRule


class TestAlertFinal:
    def test_manager_no_rules(self):
        mgr = AlertManager()
        assert mgr.evaluate({"cpu": 100}) == []

    def test_rule_eq(self):
        rule = ThresholdRule("r", "cpu", "==", 80, 0)
        assert rule.evaluate({"cpu": 80}) is not None
        assert rule.evaluate({"cpu": 81}) is None

    def test_rule_ne(self):
        rule = ThresholdRule("r", "cpu", "!=", 80, 0)
        assert rule.evaluate({"cpu": 81}) is not None
        assert rule.evaluate({"cpu": 80}) is None

    def test_rule_duration(self):
        rule = ThresholdRule("r", "cpu", ">", 80, duration=60)
        assert rule.evaluate({"cpu": 90}) is None

    def test_rule_invalid_op(self):
        rule = ThresholdRule("r", "cpu", "bad", 80, 0)
        assert rule.evaluate({"cpu": 90}) is None
