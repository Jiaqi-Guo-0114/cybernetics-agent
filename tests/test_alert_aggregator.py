"""
AlertAggregator 测试。
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent.alert.aggregator import AlertAggregator
from cybernetics_agent.alert.core import AlertEvent


def test_aggregator_count_strategy():
    """count 策略：第一个事件被抑制，等窗口结束时发送聚合统计。"""
    agg = AlertAggregator(
        group_by=["rule_name"],
        window_seconds=1.0,
        strategy="count",
    )

    evt1 = AlertEvent(rule_name="cpu_high", severity="warning", message="CPU > 80%")
    evt2 = AlertEvent(rule_name="cpu_high", severity="warning", message="CPU > 85%")
    evt3 = AlertEvent(rule_name="cpu_high", severity="warning", message="CPU > 90%")

    # 第一个被抑制（count 策略等窗口）
    result = agg.process(evt1)
    assert result is None

    # 后续同组事件也被抑制
    result = agg.process(evt2)
    assert result is None
    result = agg.process(evt3)
    assert result is None

    # 等窗口过期
    time.sleep(1.1)
    evt4 = AlertEvent(rule_name="cpu_high", severity="warning", message="CPU > 95%")
    result = agg.process(evt4)
    assert result is not None
    assert "聚合" in result.message
    assert "3" in result.message  # 3 条被聚合
    assert result.labels["_aggregated_count"] == "3"


def test_aggregator_first_strategy():
    """first 策略：只保留第一个告警。"""
    agg = AlertAggregator(
        group_by=["rule_name"],
        window_seconds=1.0,
        strategy="first",
    )

    evt1 = AlertEvent(rule_name="mem_high", severity="warning", message="MEM > 80%")
    evt2 = AlertEvent(rule_name="mem_high", severity="warning", message="MEM > 85%")

    # 第一个通过
    result = agg.process(evt1)
    assert result is not None
    assert result.message == "MEM > 80%"

    # 后续被抑制
    result = agg.process(evt2)
    assert result is None


def test_aggregator_last_strategy():
    """last 策略：窗口过期时返回最后一个告警。"""
    agg = AlertAggregator(
        group_by=["rule_name"],
        window_seconds=0.5,
        strategy="last",
    )

    evt1 = AlertEvent(rule_name="disk_full", severity="critical", message="Disk 90%")
    evt2 = AlertEvent(rule_name="disk_full", severity="critical", message="Disk 95%")

    result = agg.process(evt1)
    assert result is not None
    assert result.message == "Disk 90%"

    result = agg.process(evt2)
    assert result is None  # 被抑制

    # 窗口过期，下一个事件触发返回上次的最后一个
    time.sleep(0.6)
    evt3 = AlertEvent(rule_name="disk_full", severity="critical", message="Disk 98%")
    result = agg.process(evt3)
    assert result is not None
    assert result.message == "Disk 95%"  # 上次窗口的最后一个


def test_aggregator_different_groups():
    """不同组的告警应该独立处理。"""
    agg = AlertAggregator(
        group_by=["rule_name"],
        window_seconds=1.0,
        strategy="first",
    )

    evt1 = AlertEvent(rule_name="cpu_high", severity="warning", message="CPU")
    evt2 = AlertEvent(rule_name="mem_high", severity="warning", message="MEM")

    result1 = agg.process(evt1)
    result2 = agg.process(evt2)

    assert result1 is not None
    assert result2 is not None
    assert result1.rule_name == "cpu_high"
    assert result2.rule_name == "mem_high"


def test_aggregator_group_by_severity():
    """按 severity 分组。"""
    agg = AlertAggregator(
        group_by=["rule_name", "severity"],
        window_seconds=1.0,
        strategy="first",
    )

    evt1 = AlertEvent(rule_name="api_error", severity="warning", message="slow")
    evt2 = AlertEvent(rule_name="api_error", severity="critical", message="down")

    result1 = agg.process(evt1)
    result2 = agg.process(evt2)

    assert result1 is not None
    assert result2 is not None
    assert result1.severity == "warning"
    assert result2.severity == "critical"


def test_aggregator_flush():
    """flush() 应该返回所有待发送的聚合告警。"""
    agg = AlertAggregator(
        group_by=["rule_name"],
        window_seconds=10.0,
        strategy="count",
    )

    for i in range(5):
        agg.process(AlertEvent(rule_name="test", severity="warning", message=f"m{i}"))

    # 窗口未过期，process 返回 None
    assert agg.process(AlertEvent(rule_name="test", severity="warning", message="m5")) is None

    # flush 强制刷新
    results = agg.flush()
    assert len(results) == 1
    assert results[0].labels["_aggregated_count"] == "6"


def test_aggregator_group_by_labels():
    """按 labels 字段分组。"""
    agg = AlertAggregator(
        group_by=["labels.service"],
        window_seconds=1.0,
        strategy="first",
    )

    evt1 = AlertEvent(rule_name="err", severity="warning", message="e1", labels={"service": "api"})
    evt2 = AlertEvent(rule_name="err", severity="warning", message="e2", labels={"service": "db"})
    evt3 = AlertEvent(rule_name="err", severity="warning", message="e3", labels={"service": "api"})

    r1 = agg.process(evt1)
    r2 = agg.process(evt2)
    r3 = agg.process(evt3)

    assert r1 is not None
    assert r2 is not None
    assert r3 is None  # api 组被抑制


def test_aggregator_max_groups():
    """超过最大组数量时应该清除最早的组。"""
    agg = AlertAggregator(
        group_by=["rule_name"],
        window_seconds=100.0,
        strategy="first",
        max_groups=2,
    )

    agg.process(AlertEvent(rule_name="a", severity="warning", message=""))
    agg.process(AlertEvent(rule_name="b", severity="warning", message=""))
    agg.process(AlertEvent(rule_name="c", severity="warning", message=""))

    # 最早的组 "a" 应该被删除
    stats = agg.get_stats()
    assert stats["active_groups"] == 2


def test_aggregator_stats():
    """get_stats 应该返回正确的统计信息。"""
    agg = AlertAggregator(
        group_by=["rule_name"],
        window_seconds=10.0,
        strategy="count",
    )

    agg.process(AlertEvent(rule_name="r1", severity="warning", message=""))
    agg.process(AlertEvent(rule_name="r1", severity="warning", message=""))

    stats = agg.get_stats()
    assert stats["strategy"] == "count"
    assert stats["active_groups"] == 1
    assert stats["groups"]["rule=r1"]["count"] == 2
