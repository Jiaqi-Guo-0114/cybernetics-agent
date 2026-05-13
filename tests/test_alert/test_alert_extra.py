"""Alert 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.alert.rules import ThresholdRule


class TestAlertExtra:
    def test_rule_duration_not_met(self):
        rule = ThresholdRule("r", "cpu", ">", 80, duration=60)
        result = rule.evaluate({"cpu": 90})
        assert result is None  # 持续时间不足

    def test_rule_invalid_operator(self):
        rule = ThresholdRule("r", "cpu", "invalid", 80, 0)
        assert rule.evaluate({"cpu": 90}) is None

    def test_rule_none_metrics(self):
        rule = ThresholdRule("r", "cpu", ">", 80, 0)
        assert rule.evaluate(None) is None
