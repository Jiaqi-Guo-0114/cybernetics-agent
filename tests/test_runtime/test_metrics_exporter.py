"""
Metrics 导出测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.runtime.metrics_collector import MetricsCollector


def test_prometheus_counter_format():
    mc = MetricsCollector()
    mc.increment("tool_calls_total", labels={"tool": "search"})
    mc.increment("tool_calls_total", labels={"tool": "search"})
    mc.increment("tool_calls_total", labels={"tool": "download"})

    output = mc.to_prometheus()
    assert "# TYPE cybernetics_tool_calls_total counter" in output
    assert 'cybernetics_tool_calls_total{tool="search"} 2' in output
    assert 'cybernetics_tool_calls_total{tool="download"} 1' in output


def test_prometheus_gauge_format():
    mc = MetricsCollector()
    mc.gauge("active_sessions", 5.0, labels={"region": "us-east"})

    output = mc.to_prometheus()
    assert "# TYPE cybernetics_active_sessions gauge" in output
    assert 'cybernetics_active_sessions{region="us-east"} 5.0' in output


def test_prometheus_histogram_format():
    mc = MetricsCollector()
    mc.record("latency_seconds", 0.05, labels={"endpoint": "api"})
    mc.record("latency_seconds", 0.15, labels={"endpoint": "api"})
    mc.record("latency_seconds", 0.8, labels={"endpoint": "api"})

    output = mc.to_prometheus()
    assert "# TYPE cybernetics_latency_seconds histogram" in output
    assert 'cybernetics_latency_seconds_bucket{endpoint="api",le="0.1"} 1' in output
    assert 'cybernetics_latency_seconds_bucket{endpoint="api",le="0.25"} 2' in output
    assert 'cybernetics_latency_seconds_sum{endpoint="api"} 1.0' in output
    assert 'cybernetics_latency_seconds_count{endpoint="api"} 3' in output


def test_openmetrics_eof():
    mc = MetricsCollector()
    output = mc.to_openmetrics()
    assert output.endswith("# EOF\n")


def test_prometheus_empty():
    mc = MetricsCollector()
    output = mc.to_prometheus()
    assert isinstance(output, str)
    assert "# TYPE" not in output  # 空指标不输出 TYPE 行
