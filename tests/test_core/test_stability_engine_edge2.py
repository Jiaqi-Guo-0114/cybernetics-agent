"""StabilityEngine 最终补充"""
import sys

import pytest

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.stability_engine import StabilityEngine


class TestStabilityEngineEdgeCases2:
    def test_on_event_stage_transition(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        se.on_event(evt)

    def test_on_event_error(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        se.on_event(evt)

    def test_with_retry_once(self):
        se = StabilityEngine({}, None)
        count = [0]
        def fn():
            count[0] += 1
            if count[0] < 2:
                raise RuntimeError("fail")
            return 42
        result = se.with_retry(fn)
        assert result == 42
        assert count[0] == 2

    def test_with_retry_exhausted(self):
        se = StabilityEngine({}, None)
        with pytest.raises(RuntimeError):
            def fail():
                raise RuntimeError("fail")
            from cybernetics_agent.core.stability_engine import RetryPolicy
            se.with_retry(fail, retry_policy=RetryPolicy(max_retries=1))

    def test_with_timeout(self):
        se = StabilityEngine({}, None)
        result = se.with_timeout(lambda: 42)
        assert result == 42
