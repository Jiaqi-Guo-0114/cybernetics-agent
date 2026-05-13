"""StabilityEngine 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.stability_engine import StabilityEngine
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestStabilityEngineExtra:
    def test_on_event_llm_request(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
        se.on_event(evt)

    def test_on_event_llm_response(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"})
        se.on_event(evt)

    def test_on_event_user_input(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        se.on_event(evt)

    def test_with_retry_success(self):
        se = StabilityEngine({}, None)
        result = se.with_retry(lambda: 42)
        assert result == 42

    def test_with_timeout_success(self):
        se = StabilityEngine({}, None)
        result = se.with_timeout(lambda: 42)
        assert result == 42

    def test_degrade_with_fallback(self):
        se = StabilityEngine({}, None)
        def fail():
            raise RuntimeError("fail")
        def fallback():
            return 42
        result = se.degrade(fail, [fallback])
        assert result == 42
