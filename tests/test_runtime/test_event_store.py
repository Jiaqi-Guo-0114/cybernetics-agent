"""
EventStore 测试。
"""

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.runtime.event_store import EventStore


def test_write_and_query_events():
    """写入和查询事件。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        store.write_event("tool_call", {"tool": "search", "result": "ok"}, session_id="s1")
        time.sleep(0.01)
        store.write_event("llm_call", {"model": "gpt-4"}, session_id="s1")

        events = store.query_events(limit=10)
        assert len(events) == 2
        assert events[0]["event_type"] == "llm_call"
        assert events[1]["event_type"] == "tool_call"
        assert events[1]["payload"]["tool"] == "search"
    finally:
        os.unlink(db_path)


def test_query_by_time_range():
    """按时间范围查询。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        now = time.time()
        store.write_event("old", {}, session_id="s1")
        time.sleep(0.05)
        store.write_event("new", {}, session_id="s1")

        events = store.query_events(from_time=now + 0.03, limit=10)
        assert len(events) == 1
        assert events[0]["event_type"] == "new"
    finally:
        os.unlink(db_path)


def test_write_and_query_metrics():
    """写入和查询指标。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        store.write_metric("error_rate", 0.5, {"service": "api"})
        store.write_metric("error_rate", 0.3, {"service": "api"})
        store.write_metric("latency", 100.0)

        metrics = store.query_metrics(metric_name="error_rate", limit=10)
        assert len(metrics) == 2
        assert metrics[0]["metric_value"] == 0.3
        assert metrics[0]["labels"]["service"] == "api"
    finally:
        os.unlink(db_path)


def test_write_and_query_alerts():
    """写入和查询告警。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        store.write_alert("high_cpu", "warning", "CPU > 80%", metric_name="cpu", metric_value=85.0)
        store.write_alert("high_mem", "critical", "MEM > 90%", metric_name="mem", metric_value=95.0)

        alerts = store.query_alerts(severity="critical", limit=10)
        assert len(alerts) == 1
        assert alerts[0]["rule_name"] == "high_mem"
    finally:
        os.unlink(db_path)


def test_stats_and_prune():
    """统计和清理。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        store.write_event("e1", {})
        store.write_metric("m1", 1.0)
        store.write_alert("a1", "info", "test")

        stats = store.get_stats()
        assert stats["events"] == 1
        assert stats["metrics"] == 1
        assert stats["alerts"] == 1

        pruned = store.prune(max_age_days=0)
        assert pruned["events"] == 1
        assert pruned["metrics"] == 1
        assert pruned["alerts"] == 1

        stats = store.get_stats()
        assert stats["events"] == 0
    finally:
        os.unlink(db_path)
