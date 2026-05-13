"""AlertManager evaluate 异常路径"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.alert.manager import AlertManager

class BadRule:
    name = "bad"
    def evaluate(self, data):
        raise RuntimeError("fail")

class TestAlertManagerException:
    def test_evaluate_rule_exception(self):
        mgr = AlertManager()
        mgr.add_rule(BadRule())
        alerts = mgr.evaluate({"cpu": 100})
        assert alerts == []
