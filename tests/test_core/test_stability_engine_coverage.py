"""StabilityEngine 剩余代码补充"""
import sys

import pytest

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.stability_engine import RetryPolicy, StabilityEngine


class TestStabilityEngineCoverage:
    def test_on_event_tool_call(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        se.on_event(evt)

    def test_on_event_tool_result(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"})
        se.on_event(evt)

    def test_on_event_tool_error(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"})
        se.on_event(evt)

    def test_on_event_llm_request(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"})
        se.on_event(evt)

    def test_on_event_llm_response(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"})
        se.on_event(evt)

    def test_on_event_stage_transition(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        se.on_event(evt)

    def test_on_event_user_input(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        se.on_event(evt)

    def test_on_event_user_feedback(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        se.on_event(evt)

    def test_on_event_error(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        se.on_event(evt)

    def test_with_retry_success(self):
        se = StabilityEngine({}, None)
        result = se.with_retry(lambda: 42)
        assert result == 42

    def test_with_retry_once_fail_then_success(self):
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
            def fail():
                raise RuntimeError("fail")
            se.with_retry(fail, retry_policy=RetryPolicy(max_retries=1))

    def test_with_timeout(self):
        se = StabilityEngine({}, None)
        result = se.with_timeout(lambda: 42)
        assert result == 42

    def test_degrade_with_fallback(self):
        se = StabilityEngine({}, None)
        def primary():
            raise RuntimeError("fail")
        def fallback():
            return 42
        result = se.degrade(primary, [fallback])
        assert result == 42
