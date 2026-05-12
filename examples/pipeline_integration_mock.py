#!/usr/bin/env python3
"""
Cybernetics Agent × Pipeline 集成测试（Mock 版）。

不调用真实 API，只验证控制论层的接入逻辑。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.adapters import NativeAdapter
from cybernetics_agent.core.base import CyberneticsEvent, EventType


def mock_search(query: str, max_results: int = 3):
    """模拟搜索。"""
    return [
        {"title": f"Paper {i} on {query}", "year": 2024, "doi": f"10.xxxx/{i}"}
        for i in range(max_results)
    ]


def mock_download(paper: dict):
    """模拟下载。"""
    return {"success": True, "path": f"/tmp/{paper['doi'].replace('/', '_')}.pdf"}


def mock_generate(papers: list):
    """模拟报告生成。"""
    return f"# Systematic Review\n\nAnalyzed {len(papers)} papers."


def run_mock_pipeline():
    print("🦙 启动 Mock Pipeline 集成测试\n")

    # 创建控制论层
    config = CyberneticsConfig(
        project_name="mock-pipeline",
        feedback_loop={"enabled": True, "mode": "automatic"},
        stability={"enabled": True},
        system_id={"enabled": True},
        optimal_control={"enabled": True, "budgets": {"api_calls_per_session": 10}},
        info_flow={"enabled": True},
        adaptive={"enabled": True},
        hierarchy={"enabled": True},
    )
    ctx = CyberneticsContext(config)
    adapter = NativeAdapter(ctx)
    adapter.install(None)

    # 用装饰器包裹模拟函数
    @adapter.instrument_tool("search")
    def search(query: str, max_results: int = 3):
        return mock_search(query, max_results)

    @adapter.instrument_tool("download")
    def download(paper: dict):
        return mock_download(paper)

    @adapter.instrument_tool("generate")
    def generate(papers: list):
        return mock_generate(papers)

    # 运行 pipeline
    papers = search("mindfulness depression", max_results=3)
    print(f"   搜索结果: {len(papers)} 篇论文")

    downloaded = [download(p) for p in papers]
    print(f"   下载结果: {sum(1 for d in downloaded if d['success'])} 成功")

    report = generate(papers)
    print(f"   报告长度: {len(report)} 字符")

    # 打印状态
    print("\n" + "=" * 50)
    print("🦙 控制论层状态报告")
    print("=" * 50)

    status = ctx.get_status()
    print(f"\nSession: {status['session_id']}")
    print(f"项目: {status['project_name']}")

    print("\n┌────────────────────────────────────────────────┐")
    print("│ 事件统计                                         │")
    print("├────────────────────────────────────────────────┤")

    summary = ctx.metrics.get_summary()
    for event_name, count_data in summary.get("counters", {}).items():
        total = sum(count_data.values())
        print(f"│  {event_name:30s} {total:5d} │")
    print("└────────────────────────────────────────────────┘")

    # 模块状态
    print("\n┼ 七大原则模块")
    for mod_name in ["feedback_loop", "stability", "system_id", "optimal_control",
                      "info_flow", "adaptive", "hierarchy"]:
        mod = ctx.get_module(mod_name)
        if mod:
            st = mod.get_status()
            print(f"  ✅ {mod_name:20s} 启用={st.get('enabled', False)}")

    ctx.shutdown()
    print("\n✅ Mock Pipeline 完成！")


if __name__ == "__main__":
    run_mock_pipeline()
