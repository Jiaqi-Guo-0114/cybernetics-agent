"""StabilityEngine 测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.stability_engine import StabilityEngine, RetryPolicy
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestStabilityEngine:
    def test_init(self):
        se = StabilityEngine({}, None)
        assert isinstance(se.get_status(), dict)

    def test_initialize_shutdown(self):
        se = StabilityEngine({}, None)
        se.initialize()
        se.shutdown()

    def test_on_event(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        result = se.on_event(evt)
        assert result is not None

    def test_with_retry_success(self):
        se = StabilityEngine({}, None)
        result = se.with_retry(lambda: 42)
        assert result == 42

    def test_with_retry_failure(self):
        se = StabilityEngine({}, None)
        with pytest.raises(RuntimeError):
            se.with_retry(lambda: (_ for _ in ()).throw(RuntimeError("fail")), retry_policy=RetryPolicy(max_retries=1))

    def test_with_timeout(self):
        se = StabilityEngine({}, None)
        result = se.with_timeout(lambda: 42)
        assert result == 42

    def test_with_circuit_breaker(self):
        se = StabilityEngine({}, None)
        result = se.with_circuit_breaker("cb1", lambda: 42)
        assert result == 42

    def test_degrade(self):
        se = StabilityEngine({}, None)
        result = se.degrade(lambda: 42)
        assert result == 42

    def test_degrade_fallback(self):
        se = StabilityEngine({}, None)
        def primary():
            raise RuntimeError("fail")
        def fallback():
            return 0
        result = se.degrade(primary, [fallback])
        assert result == 0

    def test_reset_stats(self):
        se = StabilityEngine({}, None)
        se.reset_stats()
