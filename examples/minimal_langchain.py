#!/usr/bin/env python3
"""
LangChain 适配器最小示例。

展示如何将 Cybernetics 层接入 LangChain 应用，实现：
- 工具调用的自动重试与降级
- Token 使用监控
- 并行竞争策略

Usage:
    pip install langchain
    python3 examples/minimal_langchain.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.adapters import LangChainAdapter


def main() -> None:
    # 1. 创建配置（使用低成本预设保守测试）
    config = CyberneticsConfig(
        project_name="langchain-demo",
        stability={
            "enabled": True,
            "timeout": {"default": 10.0, "llm": 30.0, "tool": 10.0},
            "retry": {"max_retries": 2, "backoff": "exponential", "base_delay": 1.0, "max_delay": 10.0},
            "circuit_breaker": {"enabled": True, "failure_threshold": 3, "recovery_timeout": 30.0, "half_open_max_calls": 1},
            "graceful_degradation": {"enabled": True, "chain": ["abstract", "metadata"]},
            "parallel_competition": {"enabled": False},
        },
        optimal_control={
            "enabled": True,
            "budgets": {"tokens_per_session": 5000, "api_calls_per_session": 5, "cost_usd_per_session": 0.1},
        },
    )

    # 2. 创建上下文
    ctx = CyberneticsContext(config)

    # 3. 创建并安装适配器
    adapter = LangChainAdapter(ctx)
    adapter.install(None)  # LangChain 适配器不需要外部客户端

    print("✅ LangChain 适配器已安装")
    print(f"   会话 ID: {ctx.session_id}")
    print(f"   配置: {config.project_name}")

    # 4. 模拟工具调用
    print("\n🔧 模拟工具调用...")
    result = ctx.emit_tool_result(tool_name="web_search", result=["paper1", "paper2"])
    print(f"   结果: {result}")

    # 5. 模拟 LLM 调用
    print("\n🤖 模拟 LLM 调用...")
    ctx.emit_llm_request(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
        response={"role": "assistant", "content": "Hi!"},
    )

    # 6. 打印状态
    print("\n📊 当前状态:")
    status = ctx.get_status()
    for mod, st in status.get("modules", {}).items():
        print(f"   {mod}: {'✅' if st.get('enabled') else '❌'}")

    ctx.shutdown()
    print("\n✅ 演示完成")


if __name__ == "__main__":
    main()
