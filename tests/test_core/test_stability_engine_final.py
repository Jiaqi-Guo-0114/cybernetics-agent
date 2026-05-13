"""StabilityEngine 最终补充测试"""
import sys

import pytest

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.stability_engine import StabilityEngine


class TestStabilityEngineFinal:
    def test_tool_result_no_tool_name(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"duration": 1.0})
        se.on_event(evt)

    def test_tool_error_no_tool_name(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {})
        se.on_event(evt)

    def test_llm_request_no_model(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        se.on_event(evt)

    def test_llm_response_no_model(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        se.on_event(evt)

    def test_stage_transition_no_stages(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        se.on_event(evt)

    def test_user_input_no_text(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        se.on_event(evt)

    def test_user_feedback_no_type(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        se.on_event(evt)

    def test_error_no_error_type(self):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        se.on_event(evt)

    def test_with_retry_default_policy(self):
        se = StabilityEngine({}, None)
        result = se.with_retry(lambda: 42)
        assert result == 42

    def test_degrade_no_fallbacks(self):
        se = StabilityEngine({}, None)
        with pytest.raises(RuntimeError):
            se.degrade(lambda: (_ for _ in ()).throw(RuntimeError("fail")), [])

    def test_get_status(self):
        se = StabilityEngine({}, None)
        status = se.get_status()
        assert isinstance(status, dict)
