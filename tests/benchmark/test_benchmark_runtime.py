"""
Runtime 模块性能基准测试。

测试 EventBus、MetricsCollector、EventStore 等运行时模块的性能。
"""
import sys
sys.path.insert(0, 'src')

import pytest

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.runtime.metrics_collector import MetricsCollector
from cybernetics_agent.runtime.event_store import EventStore


class TestEventBusBenchmark:
    def test_emit_single_event(self, benchmark):
        bus = EventBus()
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        benchmark(bus.emit, evt)

    def test_emit_100_events(self, benchmark):
        bus = EventBus()
        events = [CyberneticsEvent.create(EventType.TOOL_CALL, f"s{i}", {"tool_name": "search"}) for i in range(100)]
        def emit_all():
            for evt in events:
                bus.emit(evt)
        benchmark(emit_all)

    def test_emit_with_subscriber(self, benchmark):
        bus = EventBus()
        class Sub:
            def on_event(self, event): pass
        bus.subscribe(Sub())
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        benchmark(bus.emit, evt)


class TestMetricsCollectorBenchmark:
    def test_record_single_metric(self, benchmark):
        col = MetricsCollector()
        benchmark(col.record, "latency", 0.5)

    def test_record_100_metrics(self, benchmark):
        col = MetricsCollector()
        def record_all():
            for i in range(100):
                col.record("latency", float(i) / 100.0)
        benchmark(record_all)

    def test_increment_counter(self, benchmark):
        col = MetricsCollector()
        benchmark(col.increment, "requests")

    def test_get_summary(self, benchmark):
        col = MetricsCollector()
        for i in range(1000):
            col.record("latency", float(i) / 1000.0)
        benchmark(col.get_summary)


class TestEventStoreBenchmark:
    def test_store_single_event(self, benchmark, tmp_path):
        store = EventStore(f"{tmp_path}/events.db")
        benchmark(store.write_event, "tool_call", {"tool_name": "search"})
        store.close()

    def test_query_recent(self, benchmark, tmp_path):
        store = EventStore(f"{tmp_path}/events.db")
        for i in range(100):
            store.write_event("tool_call", {"tool_name": "search"})
        benchmark(store.query_events, limit=10)
        store.close()
