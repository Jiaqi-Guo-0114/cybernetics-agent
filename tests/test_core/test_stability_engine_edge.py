"""StabilityEngine 边界条件测试"""
import sys
import time

import pytest

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.stability_engine import StabilityEngine


class TestStabilityEngineEdgeCases:
    def test_on_event_llm_request(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
        se.on_event(evt)

    def test_on_event_llm_response(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"})
        se.on_event(evt)

    def test_on_event_unknown(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        se.on_event(evt)

    def test_with_timeout_slow(self):
        se = StabilityEngine({}, None)
        def slow():
            time.sleep(0.01)
            return 42
        result = se.with_timeout(slow, timeout_type="tool")
        assert result == 42

    def test_with_circuit_breaker_error(self):
        se = StabilityEngine({}, None)
        def fail():
            raise RuntimeError("fail")
        with pytest.raises(RuntimeError):
            se.with_circuit_breaker("cb_test", fail)

    def test_degrade_no_fallback(self):
        se = StabilityEngine({}, None)
        def fail():
            raise RuntimeError("fail")
        with pytest.raises(RuntimeError):
            se.degrade(fail)

    def test_degrade_multiple_fallbacks(self):
        se = StabilityEngine({}, None)
        def fail():
            raise RuntimeError("fail")
        def fb1():
            raise RuntimeError("fb1 fail")
        def fb2():
            return 42
        result = se.degrade(fail, [fb1, fb2])
        assert result == 42
