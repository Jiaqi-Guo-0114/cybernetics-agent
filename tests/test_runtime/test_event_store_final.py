"""EventStore 最终补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.event_store import EventStore


class TestEventStoreFinal:
    def test_query_events_all_filters(self, tmp_path):
        import time
        db = str(tmp_path / "store.db")
        store = EventStore(db)
        t0 = time.time()
        store.write_event("evt", {"a": 1})
        results = store.query_events(from_time=t0 - 1, to_time=t0 + 10, event_type="evt", limit=10)
        assert len(results) == 1
        store.close()

    def test_query_metrics_all_filters(self, tmp_path):
        import time
        db = str(tmp_path / "store.db")
        store = EventStore(db)
        t0 = time.time()
        store.write_metric("cpu", 0.5, {"host": "local"})
        results = store.query_metrics(metric_name="cpu", from_time=t0 - 1, to_time=t0 + 10, limit=10)
        assert len(results) == 1
        store.close()

    def test_query_alerts_all_filters(self, tmp_path):
        import time
        db = str(tmp_path / "store.db")
        store = EventStore(db)
        t0 = time.time()
        store.write_alert("rule1", "warning", "msg")
        results = store.query_alerts(from_time=t0 - 1, to_time=t0 + 10, severity="warning", limit=10)
        assert len(results) == 1
        store.close()

    def test_prune_old_data(self, tmp_path):
        db = str(tmp_path / "store.db")
        store = EventStore(db)
        store.write_event("evt", {})
        store.write_metric("m", 1.0)
        store.write_alert("r", "warn", "msg")
        pruned = store.prune(max_age_days=0.0001)
        assert isinstance(pruned, dict)
        store.close()

    def test_default_path(self):
        store = EventStore()
        store.write_event("test", {})
        stats = store.get_stats()
        assert stats["events"] >= 1
        store.close()
