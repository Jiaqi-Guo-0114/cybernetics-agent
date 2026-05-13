"""StabilityEngine 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.stability_engine import StabilityEngine, RetryPolicy
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestStabilityEngineExtra:
    def test_on_event_tool_result(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"})
        se.on_event(evt)

    def test_on_event_tool_error(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search", "error": "timeout"})
        se.on_event(evt)

    def test_with_retry_once(self):
        se = StabilityEngine({}, None)
        count = [0]
        def fn():
            count[0] += 1
            if count[0] < 2:
                raise RuntimeError("fail")
            return 42
        result = se.with_retry(fn, retry_policy=RetryPolicy(max_retries=3))
        assert result == 42
        assert count[0] == 2

    def test_with_retry_exhausted(self):
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
        def primary():
            raise RuntimeError("fail")
        def fallback():
            return 0
        result = se.degrade(primary, [fallback])
        assert result == 0

    def test_reset_stats(self):
        se = StabilityEngine({}, None)
        se.reset_stats()

