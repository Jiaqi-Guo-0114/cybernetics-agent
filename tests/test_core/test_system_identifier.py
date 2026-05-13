"""SystemIdentifier 测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestSystemIdentifier:
    def test_init(self):
        si = SystemIdentifier({}, None)
        assert isinstance(si.get_status(), dict)

    def test_initialize_shutdown(self):
        si = SystemIdentifier({}, None)
        si.initialize()
        si.shutdown()

    def test_on_event(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        result = si.on_event(evt)
        assert result is not None

    def test_get_tool_performance(self):
        si = SystemIdentifier({}, None)
        perf = si.get_tool_performance()
        assert isinstance(perf, dict)

    def test_predict_performance(self):
        si = SystemIdentifier({}, None)
        pred = si.predict_performance()
        assert isinstance(pred, dict)

    def test_get_conversion_funnel(self):
        si = SystemIdentifier({}, None)
        funnel = si.get_conversion_funnel(["stage1", "stage2"])
        assert isinstance(funnel, dict)
