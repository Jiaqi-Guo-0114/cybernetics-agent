"""AlertManager 最终补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.alert.manager import AlertManager
from cybernetics_agent.alert.rules import ThresholdRule
from cybernetics_agent.alert.core import AlertEvent

class MockRuleNoEvaluate:
    name = "no_eval"

class MockChannelBad:
    def health_check(self):
        return False
    def send(self, event):
        raise RuntimeError("fail")

class TestAlertManagerFinal:
    def test_unregister_nonexistent(self):
        mgr = AlertManager()
        assert mgr.unregister_channel("nonexistent") is False

    def test_evaluate_no_evaluate_attr(self):
        mgr = AlertManager()
        mgr.add_rule(MockRuleNoEvaluate())
        alerts = mgr.evaluate({"cpu": 100})
        assert alerts == []

    def test_evaluate_with_event_store(self):
        class FakeStore:
            def write_alert(self, **kwargs): pass
        mgr = AlertManager(event_store=FakeStore())
        mgr.add_rule(ThresholdRule("r", "cpu", ">", 0, 0))
        alerts = mgr.evaluate({"cpu": 100})
        assert len(alerts) >= 1

    def test_evaluate_event_store_fail(self):
        class BadStore:
            def write_alert(self, **kwargs):
                raise RuntimeError("fail")
        mgr = AlertManager(event_store=BadStore())
        mgr.add_rule(ThresholdRule("r", "cpu", ">", 0, 0))
        alerts = mgr.evaluate({"cpu": 100})
        assert len(alerts) >= 1

    def test_dispatch_missing_channel(self):
        mgr = AlertManager()
        evt = AlertEvent("r", "warning", "test")
        results = mgr.dispatch(evt, ["missing"])
        assert results.get("missing") is False

    def test_dispatch_channel_exception(self):
        mgr = AlertManager()
        mgr.register_channel("bad", MockChannelBad())
        evt = AlertEvent("r", "warning", "test")
        results = mgr.dispatch(evt, ["bad"])
        assert results.get("bad") is False
