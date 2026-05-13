#!/usr/bin/env python3
"""
Hermes 适配器最小示例。

将 Cybernetics 层接入 Hermes Agent 工作流，实现：
- 工具调用间的自动重试
- 会话级资源管理
- 回复质量监控

Usage:
    python3 examples/minimal_hermes.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.adapters import HermesAdapter
from cybernetics_agent.presets import apply_preset


def main() -> None:
    # 1. 使用高可靠性预设
    base = CyberneticsConfig(project_name="hermes-demo")
    config = apply_preset(base, "high_reliability")

    # 2. 创建上下文
    ctx = CyberneticsContext(config)

    # 3. 安装 Hermes 适配器
    adapter = HermesAdapter(ctx)
    adapter.install(None)

    print("✅ Hermes 适配器已安装")
    print(f"   会话 ID: {ctx.session_id}")
    print(f"   预设: high_reliability")

    # 4. 模拟 Hermes 工具调用
    print("\n🔧 模拟 Hermes 工具调用...")
    for tool in ("web_search", "file_read", "terminal"):
        result = ctx.emit_tool_result(
            tool_name=tool,
            result={"status": "success", "tool": tool},
        )
        print(f"   {tool}: {result}")

    # 5. 模拟多轮对话
    print("\n💬 模拟对话轮次...")
    for turn in range(2):
        ctx.emit_llm_request(
            model="kimi-k2-5",
            messages=[{"role": "user", "content": f"Turn {turn}"}],
            response={"role": "assistant", "content": f"Response {turn}"},
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
