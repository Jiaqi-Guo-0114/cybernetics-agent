"""最终补充测试 - 覆盖边缘情况"""
import pytest
import sys, time
sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.circuit_breaker import CircuitBreaker
from cybernetics_agent.core.stage_metrics import StageMetrics
from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.alert.rules import ThresholdRule
from cybernetics_agent.alert.manager import AlertManager
from cybernetics_agent.presets import list_presets, get_preset

class TestFinalEdgeCases:
    # base.py 行 128, 137
    def test_event_type_str(self):
        assert str(EventType.TOOL_CALL) == "EventType.TOOL_CALL"

    # circuit_breaker.py 行 62, 90
    def test_circuit_breaker_half_open_then_close(self):
        import time
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01, half_open_max_calls=1)
        cb.record_failure()
        assert cb.can_execute() is False
        time.sleep(0.02)
        assert cb.can_execute() is True  # half_open
        cb.record_success()
        assert cb.can_execute() is True  # closed

    # stage_metrics.py 行 28, 49
    def test_stage_metrics_empty(self):
        sm = StageMetrics("s1")
        assert sm.avg_duration == 0.0
        assert sm.p95_duration == 0.0

    # event_bus.py 行 63-64, 88, 95
    def test_event_bus_get_stats(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        stats = bus.get_stats()
        assert "tool_call" in stats

    # presets.py 行 136-150
    def test_preset_apply(self):
        from cybernetics_agent.presets import apply_preset
        from cybernetics_agent.config import CyberneticsConfig
        cfg = CyberneticsConfig()
        for name in list_presets():
            result = apply_preset(cfg, name)
            assert isinstance(result.to_dict(), dict)

    # alert/rules.py 行 68, 87
    def test_rule_duration(self):
        rule = ThresholdRule("r", "cpu", ">", 80, duration=0.001)
        rule.evaluate({"cpu": 90})
        time.sleep(0.002)
        result = rule.evaluate({"cpu": 90})
        assert result is not None

    # alert/manager.py 行 48, 59, 66-76, 90-91, 94-95
    def test_alert_manager_evaluate(self):
        mgr = AlertManager()
        mgr.add_rule(ThresholdRule("r", "cpu", ">", 0, 0))
        alerts = mgr.evaluate({"cpu": 100})
        assert isinstance(alerts, list)
