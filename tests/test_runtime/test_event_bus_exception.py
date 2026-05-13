"""EventBus 异常路径"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class BadSub:
    def on_event(self, event):
        raise RuntimeError("fail")

class TestEventBusException:
    def test_emit_subscriber_exception(self):
        bus = EventBus()
        bus.subscribe(BadSub())
        try:
            bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        except RuntimeError:
            pass
