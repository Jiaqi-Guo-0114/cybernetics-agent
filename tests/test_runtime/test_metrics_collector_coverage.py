"""MetricsCollector 剩余代码补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.metrics_collector import MetricsCollector
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestMetricsCollectorCoverage:
    def test_raw_events_prune(self):
        col = MetricsCollector()
        for i in range(6000):
            col.record("x", float(i))
        assert len(col._raw_events) <= 3000

    def test_llm_error_event(self):
        col = MetricsCollector()
        evt = CyberneticsEvent.create(EventType.LLM_ERROR, "s1", {"model": "gpt-4"})
        col.record_event(evt)
        s = col.get_summary()
        assert "llm_errors_total" in s.get("counters", {})

    def test_error_with_type(self):
        col = MetricsCollector()
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {"error_type": "TimeoutError"})
        col.record_event(evt)
        s = col.get_summary()
        assert "errors_total" in s.get("counters", {})

    def test_event_store_persist(self):
        class FakeStore:
            def write_event(self, **kwargs): pass
        col = MetricsCollector(FakeStore())
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        col.record_event(evt)

    def test_event_store_persist_fail(self):
        class BadStore:
            def write_event(self, **kwargs):
                raise RuntimeError("fail")
        col = MetricsCollector(BadStore())
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
        col.record_event(evt)

    def test_empty_histogram_skip(self):
        col = MetricsCollector()
        col._histograms["test"] = {"": []}
        s = col.get_summary()
        # 空 values 会被跳过，但 histogram 项仍然存在（只是内部为空）
        assert "test" in s.get("histograms", {})

    def test_llm_success_rate(self):
        col = MetricsCollector()
        col.increment("llm_calls_total", labels={"model": "gpt-4"})
        col.increment("llm_errors_total", labels={"model": "gpt-4"})
        s = col.get_summary()
        assert "llm_success_rate" in s

    def test_conversion_funnel(self):
        col = MetricsCollector()
        funnel = col.get_conversion_funnel(["s1", "s2", "s3"])
        assert isinstance(funnel, dict)

    def test_conversion_funnel_with_session(self):
        col = MetricsCollector()
        funnel = col.get_conversion_funnel(["s1", "s2"], session_id="test")
        assert isinstance(funnel, dict)

    def test_reset(self):
        col = MetricsCollector()
        col.increment("x")
        col.gauge("y", 1.0)
        col.record("z", 1.0)
        col.reset()
        s = col.get_summary()
        assert s == {"counters": {}, "gauges": {}, "histograms": {}}

    def test_gauge_no_labels(self):
        col = MetricsCollector()
        col.gauge("temp", 25.0)
        s = col.get_summary()
        assert "temp" in s.get("gauges", {})

    def test_prometheus_gauge_no_labels(self):
        col = MetricsCollector()
        col.gauge("temp", 25.0)
        out = col.to_prometheus("app")
        assert "app_temp" in out

    def test_prometheus_histogram_no_labels(self):
        col = MetricsCollector()
        col.record("latency", 0.5)
        out = col.to_prometheus("app")
        assert "app_latency_sum" in out
        assert "app_latency_count" in out

    def test_openmetrics(self):
        col = MetricsCollector()
        out = col.to_openmetrics("app")
        assert "# EOF" in out
