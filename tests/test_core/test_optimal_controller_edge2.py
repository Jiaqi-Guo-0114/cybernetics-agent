"""OptimalController 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.optimal_controller import OptimalController
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestOptimalControllerEdgeCases:
    def test_on_event_stage_transition(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {})
        oc.on_event(evt)

    def test_on_event_error(self):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        oc.on_event(evt)

    def test_can_afford_no_pool(self):
        oc = OptimalController({}, None)
        assert oc.can_afford("nonexistent", 0.0) is True

    def test_get_fallback(self):
        oc = OptimalController({}, None)
        strategy = oc.get_fallback_strategy()
        assert isinstance(strategy, dict)

    def test_check_rate_limits(self):
        oc = OptimalController({}, None)
        assert isinstance(oc.check_llm_rate_limit(), bool)
        assert isinstance(oc.check_tool_concurrency(), bool)
