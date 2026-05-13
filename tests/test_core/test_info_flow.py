"""InfoFlow 测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.info_flow import InfoFlow
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestInfoFlow:
    def test_init(self):
        iflow = InfoFlow({}, None)
        assert isinstance(iflow.get_status(), dict)

    def test_initialize_shutdown(self):
        iflow = InfoFlow({}, None)
        iflow.initialize()
        iflow.shutdown()

    def test_on_event(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        result = iflow.on_event(evt)
        assert result is not None
