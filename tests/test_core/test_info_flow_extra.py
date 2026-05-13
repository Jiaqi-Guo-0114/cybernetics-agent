"""InfoFlow 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.info_flow import InfoFlow


class TestInfoFlowExtra:
    def test_on_event(self):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        iflow.on_event(evt)

    def test_initialize_shutdown(self):
        iflow = InfoFlow({}, None)
        iflow.initialize()
        iflow.shutdown()


    def test_enabled_toggle(self):
        iflow = InfoFlow({}, None)
        iflow.enabled = False
        assert iflow.enabled is False
        iflow.enabled = True
        assert iflow.enabled is True
