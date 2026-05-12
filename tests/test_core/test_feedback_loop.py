"""
反馈闭环模块的 pytest 测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core import FeedbackLoop
from cybernetics_agent.core.base import CyberneticsEvent, EventType


@pytest.fixture
def feedback_loop():
    config = {
        "enabled": True,
        "mode": "automatic",
        "actions": [
            {"trigger": "tool_error_rate > 0.3", "action": "retry"},
            {"trigger": "feedback_depth >= 2", "action": "abort"},
        ],
        "max_feedback_depth": 3,
    }
    ctx = CyberneticsContext(CyberneticsConfig())
    fb = FeedbackLoop(config, ctx)
    fb.initialize()
    return fb


def test_initialization(feedback_loop):
    assert feedback_loop.name == "feedback_loop"
    assert len(feedback_loop._rules) == 2
    assert feedback_loop._max_depth == 3


def test_event_processing(feedback_loop):
    evt = CyberneticsEvent.create(
        EventType.TOOL_RESULT, "s1", {"tool_name": "search", "success": False}
    )
    feedback_loop.on_event(evt)
    assert feedback_loop._tool_calls == 1
    assert feedback_loop._tool_errors == 1


def test_trigger_evaluation(feedback_loop):
    ctx = {"tool_error_rate": 0.5, "feedback_depth": 0.0}
    assert feedback_loop._evaluate_trigger("tool_error_rate > 0.3", ctx) is True
    assert feedback_loop._evaluate_trigger("tool_error_rate <= 0.3", ctx) is False
    assert feedback_loop._evaluate_trigger("feedback_depth < 3", ctx) is True


def test_max_depth_limit(feedback_loop):
    feedback_loop._current_depth = 3
    feedback_loop._evaluate_rules()
    assert len(feedback_loop.get_actions()) == 0


def test_status_report(feedback_loop):
    # 发送 1 个失败事件触发一次反馈
    feedback_loop.on_event(CyberneticsEvent.create(
        EventType.TOOL_RESULT, "s1", {"success": False}
    ))
    status = feedback_loop.get_status()
    assert status["tool_error_rate"] == 1.0
    assert status["current_depth"] == 1
