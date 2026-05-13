"""补齐 info_flow.py 未覆盖分支 — 过滤器解析、去重、速率限制、路由。"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.info_flow import InfoFlow


class TestInfoFlowBranches:
    def test_filter_parsing_without_type(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={"filters": [{}]}, ctx=ctx)
        assert ifl._filters[0]["type"] == "deduplicate"
        assert ifl._filters[0]["params"] == {}

    def test_dedup_window_seconds_from_config(self):
        ctx = MagicMock()
        ifl = InfoFlow(
            config={"filters": [{"type": "deduplicate", "params": {"window_seconds": 10.0}}]},
            ctx=ctx,
        )
        assert ifl._dedup_window_seconds == 10.0

    def test_rate_limit_max_from_config(self):
        ctx = MagicMock()
        ifl = InfoFlow(
            config={"filters": [{"type": "rate_limit", "params": {"max_events_per_second": 50}}]},
            ctx=ctx,
        )
        assert ifl._rate_limit_max == 50

    def test_duplicate_event_returns_none(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.TOOL_ERROR, "sess-01",
            payload={"tool_name": "search"},
        )
        assert ifl.on_event(event) is event  # first pass
        assert ifl.on_event(event) is None    # duplicate dropped
        assert ifl._deduped_count == 1

    def test_duplicate_with_error_type(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.ERROR, "sess-01",
            payload={"error_type": "timeout"},
        )
        assert ifl.on_event(event) is event
        assert ifl.on_event(event) is None
        assert ifl._dedup_window["error|sess-01|timeout"].count == 2

    def test_should_route_false(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={"channels": ["metrics"]}, ctx=ctx)
        event = CyberneticsEvent.create(EventType.AGENT_START, "s")
        assert ifl.on_event(event) is None
        assert ifl._filtered_count == 1

    def test_rate_limit_throttled(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={"filters": [{"type": "rate_limit", "params": {"max_events_per_second": 2}}]}, ctx=ctx)
        # use different payloads to avoid dedup
        for i in range(3):
            event = CyberneticsEvent.create(EventType.AGENT_START, f"s{i}")
            result = ifl.on_event(event)
            if i < 2:
                assert result is event
            else:
                assert result is event  # throttled but returned
        assert ifl._throttled_count == 1

    def test_rate_limit_window_cleanup(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={}, ctx=ctx)
        # inject old timestamps
        ifl._rate_limit_window = [time.time() - 2.0, time.time() - 1.5]
        event = CyberneticsEvent.create(EventType.AGENT_START, "s")
        ifl.on_event(event)
        # old entries cleaned, new one added
        assert len(ifl._rate_limit_window) == 1

    def test_dedup_window_cleanup(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={"filters": [{"type": "deduplicate", "params": {"window_seconds": 0.1}}]}, ctx=ctx)
        event = CyberneticsEvent.create(EventType.TOOL_CALL, "s", payload={"tool_name": "t1"})
        ifl.on_event(event)
        time.sleep(0.15)
        # old entry expired
        assert ifl.on_event(event) is event

    def test_get_status(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={}, ctx=ctx)
        status = ifl.get_status()
        assert status["enabled"] is True
        assert status["max_eps"] == 100
        assert status["dedup_window_size"] == 0

    def test_default_channels(self):
        ctx = MagicMock()
        ifl = InfoFlow(config={}, ctx=ctx)
        assert ifl._channels == ["event_bus", "metrics", "storage"]
