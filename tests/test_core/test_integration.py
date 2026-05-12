"""核心模块集成测试。

验证七大原则模块可以协同工作。
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core import (
    AdaptiveTuner,
    EventType,
    FeedbackLoop,
    HierarchyController,
    InfoFlow,
    OptimalController,
    StabilityEngine,
    SystemIdentifier,
)
from cybernetics_agent.core.base import CyberneticsEvent


def test_all_modules_integration():
    """所有模块集成测试。"""
    # 创建配置
    config = CyberneticsConfig.from_dict({
        "project_name": "integration-test",
        "feedback_loop": {"enabled": True, "actions": [], "max_feedback_depth": 2},
        "stability": {"enabled": True},
        "system_id": {"enabled": True},
        "optimal_control": {"enabled": True},
        "info_flow": {"enabled": True, "filters": []},
        "adaptive": {"enabled": True},
        "hierarchy": {"enabled": True},
    })
    config_dict = config.to_dict()

    # 创建上下文
    ctx = CyberneticsContext(config)

    # 注册所有模块
    modules = [
        FeedbackLoop(config_dict["feedback_loop"], ctx),
        StabilityEngine(config_dict["stability"], ctx),
        SystemIdentifier(config_dict["system_id"], ctx),
        OptimalController(config_dict["optimal_control"], ctx),
        InfoFlow(config_dict["info_flow"], ctx),
        AdaptiveTuner(config_dict["adaptive"], ctx),
        HierarchyController(config_dict["hierarchy"], ctx),
    ]

    for mod in modules:
        ctx.register_module(mod)

    assert len(ctx.get_all_modules()) == 7
    print("  ✅ 注册了 7 个模块")

    # 模拟 Agent 工作流
    # 1. Agent 启动
    ctx.emit(CyberneticsEvent.create(EventType.AGENT_START, ctx.session_id, {"task": "research"}))

    # 2. LLM 请求
    ctx.emit_llm_request("gpt-4", prompt_tokens=500)
    ctx.emit_llm_response("gpt-4", completion_tokens=200, duration=2.5)

    # 3. 工具调用
    ctx.emit_tool_result("search", ["paper1", "paper2"], success=True, duration=1.0)
    ctx.emit_tool_result("download", "pdf_content", success=False, duration=3.0)
    ctx.emit_tool_error("download", "timeout", error_type="transient")

    # 4. 阶段转化
    ctx.emit(CyberneticsEvent.create(
        EventType.STAGE_TRANSITION, ctx.session_id,
        {"stage": "search", "success": True, "duration": 2.0}
    ))
    ctx.emit(CyberneticsEvent.create(
        EventType.STAGE_TRANSITION, ctx.session_id,
        {"stage": "download", "success": False, "duration": 5.0}
    ))

    # 5. 用户反馈
    ctx.emit(CyberneticsEvent.create(
        EventType.USER_FEEDBACK, ctx.session_id,
        {"type": "rating", "rating": 4, "output_id": "out_001"}
    ))

    # 6. Agent 结束
    ctx.emit(CyberneticsEvent.create(EventType.AGENT_END, ctx.session_id, {}))

    # 验证各模块状态
    status = ctx.get_status()
    assert "modules" in status
    assert "metrics" in status
    print("  ✅ 状态报告正常")

    # 验证系统辨识数据
    si = ctx.get_module("system_id")
    assert si is not None
    assert "search" in si._stage_metrics
    print("  ✅ 系统辨识采集了数据")

    # 验证最优控制消耗
    oc = ctx.get_module("optimal_control")
    assert oc is not None
    assert oc._pools["tokens"].consumed > 0
    assert oc._pools["api_calls"].consumed > 0
    print("  ✅ 最优控制记录了消耗")

    # 验证分层控制记录
    hc = ctx.get_module("hierarchy")
    assert hc is not None
    assert hc._decision_count > 0
    print("  ✅ 分层控制记录了决策")

    # 关闭
    ctx.shutdown()
    print("  ✅ 上下文关闭正常")

    print("\n  ✅ 集成测试通过！所有 7 个模块协同工作正常。")


if __name__ == "__main__":
    test_all_modules_integration()
