"""
EventStore 批量写入和 WAL 模式测试。
"""

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.runtime.event_store import EventStore


def test_batch_context_manager():
    """批量上下文管理器：with 块内写入延迟 commit。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        with store.batch():
            store.write_event("e1", {"k": 1})
            store.write_event("e2", {"k": 2})
            store.write_metric("m1", 1.0)
            store.write_alert("a1", "info", "test")
            # 在 with 块内应该还没 commit
            events = store.query_events(limit=10)
            # WAL 模式下未 commit 的数据在当前连接可见，但是我们用的是同一个连接，所以可见
            # 这里不做强勁断言，主要验证退出后数据存在

        # 退出后数据应该全部可查
        events = store.query_events(limit=10)
        assert len(events) == 2
        metrics = store.query_metrics(limit=10)
        assert len(metrics) == 1
        alerts = store.query_alerts(limit=10)
        assert len(alerts) == 1
    finally:
        os.unlink(db_path)


def test_batch_nested():
    """嵌套批量模式：只有最外层才 commit。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        with store.batch():
            store.write_event("outer", {})
            with store.batch():
                store.write_event("inner", {})
            # 内层退出不应 commit

        # 外层退出后所有数据都在
        events = store.query_events(limit=10)
        assert len(events) == 2
    finally:
        os.unlink(db_path)


def test_write_events_batch():
    """批量写入事件 API。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        events = [
            {"event_type": "click", "payload": {"id": i}}
            for i in range(100)
        ]
        store.write_events_batch(events, session_id="sess_1")

        queried = store.query_events(limit=200)
        assert len(queried) == 100
        assert queried[0]["payload"]["id"] == 99
        assert queried[99]["payload"]["id"] == 0
        assert queried[0]["session_id"] == "sess_1"
    finally:
        os.unlink(db_path)


def test_write_metrics_batch():
    """批量写入指标 API。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        metrics = [
            {"metric_name": "latency", "metric_value": float(i), "labels": {"region": "us"}}
            for i in range(50)
        ]
        store.write_metrics_batch(metrics)

        queried = store.query_metrics(metric_name="latency", limit=100)
        assert len(queried) == 50
        assert queried[0]["metric_value"] == 49.0
        assert queried[0]["labels"]["region"] == "us"
    finally:
        os.unlink(db_path)


def test_write_alerts_batch():
    """批量写入告警 API。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        alerts = [
            {
                "rule_name": f"rule_{i}",
                "severity": "warning" if i % 2 == 0 else "critical",
                "message": f"msg {i}",
                "metric_name": "cpu",
                "metric_value": float(i),
            }
            for i in range(30)
        ]
        store.write_alerts_batch(alerts)

        queried = store.query_alerts(severity="critical", limit=100)
        assert len(queried) == 15
    finally:
        os.unlink(db_path)


def test_single_write_still_works():
    """单条写入仍然正常工作（向后兼容）。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        store.write_event("single", {"key": "value"})
        store.write_metric("m", 1.0)
        store.write_alert("a", "info", "single")

        assert len(store.query_events(limit=10)) == 1
        assert len(store.query_metrics(limit=10)) == 1
        assert len(store.query_alerts(limit=10)) == 1
    finally:
        os.unlink(db_path)


def test_wal_mode_enabled():
    """WAL 模式已启用。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        conn = store._ensure_conn()
        result = conn.execute("PRAGMA journal_mode").fetchone()
        assert result[0].lower() == "wal"
    finally:
        os.unlink(db_path)


def test_batch_performance_improvement():
    """批量模式性能优于单条写入。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        store = EventStore(db_path)
        n = 200

        # 批量写入耗时
        t0 = time.perf_counter()
        with store.batch():
            for i in range(n):
                store.write_event("perf", {"i": i})
        batch_time = time.perf_counter() - t0

        # 单条写入耗时
        t0 = time.perf_counter()
        for i in range(n):
            store.write_event("perf_single", {"i": i})
        single_time = time.perf_counter() - t0

        # 批量应该明显更快（至少 2 倍）
        assert batch_time < single_time * 0.5, (
            f"batch 应该更快: batch={batch_time:.3f}s, single={single_time:.3f}s"
        )
    finally:
        os.unlink(db_path)
