"""核心模块性能基准测试。

测试各个核心模块在事件处理方面的性能表现。
"""
import sys
sys.path.insert(0, 'src')

import pytest

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.feedback_loop import FeedbackLoop
from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.optimal_controller import OptimalController
from cybernetics_agent.core.stability_engine import StabilityEngine
from cybernetics_agent.core.hierarchy_controller import HierarchyController
from cybernetics_agent.core.info_flow import InfoFlow


# ---------------------------------------------------------------------------
# 单事件处理基准
# ---------------------------------------------------------------------------

class TestFeedbackLoopBenchmark:
    def test_single_event(self, benchmark):
        fl = FeedbackLoop({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        benchmark(fl.on_event, evt)

    def test_batch_100_events(self, benchmark):
        fl = FeedbackLoop({}, None)
        events = [CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}) for _ in range(100)]
        def process():
            for evt in events:
                fl.on_event(evt)
        benchmark(process)


class TestSystemIdentifierBenchmark:
    def test_single_event(self, benchmark):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        benchmark(si.on_event, evt)

    def test_batch_100_events(self, benchmark):
        si = SystemIdentifier({}, None)
        events = [CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}) for _ in range(100)]
        def process():
            for evt in events:
                si.on_event(evt)
        benchmark(process)


class TestAdaptiveTunerBenchmark:
    def test_single_event(self, benchmark):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        benchmark(at.on_event, evt)

    def test_auto_tune(self, benchmark):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 10, "min": 1, "max": 100}]}, None)
        for _ in range(50):
            at.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 0.5}))
        benchmark(at.auto_tune)


class TestOptimalControllerBenchmark:
    def test_single_event(self, benchmark):
        oc = OptimalController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        benchmark(oc.on_event, evt)

    def test_budget_check(self, benchmark):
        oc = OptimalController({}, None)
        benchmark(oc.get_budget_status)


class TestStabilityEngineBenchmark:
    def test_single_event(self, benchmark):
        se = StabilityEngine({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        benchmark(se.on_event, evt)

    def test_with_retry(self, benchmark):
        se = StabilityEngine({}, None)
        def fn():
            return 42
        benchmark(se.with_retry, fn)


class TestHierarchyControllerBenchmark:
    def test_single_event(self, benchmark):
        hc = HierarchyController({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        benchmark(hc.on_event, evt)

    def test_make_decision(self, benchmark):
        hc = HierarchyController({}, None)
        benchmark(hc.make_decision, "layer1", "action", {"x": 1})


class TestInfoFlowBenchmark:
    def test_single_event(self, benchmark):
        iflow = InfoFlow({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        benchmark(iflow.on_event, evt)

    def test_batch_100_events(self, benchmark):
        iflow = InfoFlow({}, None)
        events = [CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}) for _ in range(100)]
        def process():
            for evt in events:
                iflow.on_event(evt)
        benchmark(process)
