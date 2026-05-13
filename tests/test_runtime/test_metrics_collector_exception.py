"""MetricsCollector 异常路径"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.metrics_collector import MetricsCollector


class TestMetricsCollectorException:
    def test_record_nan(self):
        col = MetricsCollector()
        import math
        col.record("latency", math.nan)
        s = col.get_summary()
        assert "latency" in s.get("histograms", {})
