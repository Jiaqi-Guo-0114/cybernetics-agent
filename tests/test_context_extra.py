"""Context 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestContextExtra:
    def test_get_status(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        status = ctx.get_status()
        assert "session_id" in status
        ctx.shutdown()

    def test_emit(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        from cybernetics_agent.core.base import CyberneticsEvent, EventType
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, ctx.session_id, {})
        ctx.emit(evt)
        ctx.shutdown()
