"""EventBus 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestEventBusFinal:
    def test_emit_no_handler(self):
        bus = EventBus()
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {})
        bus.emit(evt)
        assert len(bus.get_recent_events()) == 1

    def test_clear(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        bus.clear_log()
        assert bus.get_recent_events() == []
