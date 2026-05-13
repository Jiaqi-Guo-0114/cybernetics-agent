#!/usr/bin/env python3
"""
Native 适配器最小示例。

纯 Python 使用 Cybernetics 层，无需任何第三方框架。适合：
- 快速原型验证
- 脚本/工具增强
- 单独使用控制论原语

Usage:
    python3 examples/minimal_native.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.adapters import NativeAdapter
from cybernetics_agent.presets import apply_preset


def main() -> None:
    # 1. 从预设创建配置
    base = CyberneticsConfig(project_name="native-demo")
    config = apply_preset(base, "debug")  # 使用调试预设

    # 2. 创建上下文
    ctx = CyberneticsContext(config)

    # 3. 安装 Native 适配器（不需要外部客户端）
    adapter = NativeAdapter(ctx)
    adapter.install(None)

    print("✅ Native 适配器已安装")
    print(f"   会话 ID: {ctx.session_id}")
    print(f"   预设: debug")

    # 4. 发射事件
    print("\n📡 模拟数据流...")
    for i in range(3):
        ctx.emit_tool_result(
            tool_name=f"tool_{i}",
            result={"status": "ok", "index": i},
        )

    # 5. 模拟错误
    print("\n⚠️  模拟错误事件...")
    ctx.emit_tool_result(
        tool_name="risky_tool",
        result={"error": "connection timeout"},
        is_error=True,
    )

    # 6. 打印统计
    print("\n📊 实时统计:")
    status = ctx.get_status()
    print(f"   模块状态: {status.get('modules', {})}")

    ctx.shutdown()
    print("\n✅ 演示完成")


if __name__ == "__main__":
    main()
