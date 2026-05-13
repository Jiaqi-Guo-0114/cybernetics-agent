"""综合最终补充测试"""
import pytest
import sys, time
sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.feedback_loop import FeedbackLoop
from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner
from cybernetics_agent.core.hierarchy_controller import HierarchyController
from cybernetics_agent.core.info_flow import InfoFlow
from cybernetics_agent.core.optimal_controller import OptimalController
from cybernetics_agent.core.stability_engine import StabilityEngine
from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.runtime.metrics_collector import MetricsCollector
from cybernetics_agent.runtime.config_watcher import ConfigWatcher
from cybernetics_agent.runtime.plugin_loader import PluginLoader
from cybernetics_agent.runtime.state_manager import StateManager

class TestComprehensiveFinal:
    # config.py 剩余行
    def test_config_load_paths(self, tmp_path):
        import json
        # JSON 格式
        path = tmp_path / "cfg.json"
        path.write_text(json.dumps({"project_name": "json_test"}))
        cfg = CyberneticsConfig.from_json(str(path))
        assert cfg.project_name == "json_test"

    def test_config_defaults(self):
        cfg = CyberneticsConfig()
        assert cfg.project_name == "unnamed-project"

    # context.py 剩余行
    def test_context_all_event_types(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        # TOOL_RESULT
        ctx.emit_tool_result("search", ["r1"])
        # TOOL_ERROR
        ctx.emit_tool_error("search", "timeout")
        # LLM_REQUEST
        ctx.emit_llm_request("gpt-4", 100)
        # LLM_RESPONSE
        ctx.emit_llm_response("gpt-4", 50, 0.5)
        ctx.shutdown()

    def test_context_stage_transition(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, ctx.session_id, {"from_stage": "s1", "to_stage": "s2"})
        ctx.emit(evt)
        ctx.shutdown()

    # system_identifier.py 剩余行
    def test_si_all_event_types(self):
        si = SystemIdentifier({}, None)
        si.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}))
        si.on_event(CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"}))
        si.on_event(CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"}))
        si.on_event(CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4"}))
        si.on_event(CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "s1", "to_stage": "s2"}))
        si.on_event(CyberneticsEvent.create(EventType.USER_INPUT, "s1", {"text": "hello"}))
        si.on_event(CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "rating", "rating": 5}))

    # feedback_loop.py 剩余行
    def test_fl_all_event_types(self):
        fl = FeedbackLoop({}, None)
        fl.on_event(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"}))
        fl.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"}))
        fl.on_event(CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"}))
        fl.on_event(CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {}))
        fl.on_event(CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {}))
        fl.on_event(CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {}))
        fl.on_event(CyberneticsEvent.create(EventType.USER_INPUT, "s1", {}))
        fl.on_event(CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "correction"}))
        fl.on_event(CyberneticsEvent.create(EventType.ERROR, "s1", {}))

    # adaptive_tuner.py 剩余行
    def test_at_all_event_types(self):
        at = AdaptiveTuner({"parameters": [{"name": "x", "base": 0}]}, None)
        at.on_event(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"}))
        at.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}))
        at.on_event(CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search"}))
        at.on_event(CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {}))
        at.on_event(CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {}))
        at.on_event(CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {}))
        at.on_event(CyberneticsEvent.create(EventType.USER_INPUT, "s1", {}))
        at.on_event(CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "correction"}))

    # metrics_collector.py 剩余行
    def test_mc_all_types(self):
        col = MetricsCollector()
        col.record("latency", 0.5)
        col.increment("calls")
        col.increment("calls", labels={"method": "GET"})
        s = col.get_summary()
        assert "histograms" in s
        assert "counters" in s

    def test_mc_prometheus(self):
        col = MetricsCollector()
        col.record("latency", 0.5, labels={"region": "us"})
        col.increment("requests", labels={"method": "GET"})
        out = col.to_prometheus("app")
        assert len(out) > 0
