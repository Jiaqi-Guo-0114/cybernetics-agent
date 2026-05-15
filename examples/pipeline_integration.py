#!/usr/bin/env python3
"""
Cybernetics Agent × Pipeline 集成示例。

将控制论层接入 pipeline，实现自动故障检测与恢复、阶段转化率监控、资源消耗跟踪。

Usage:
    PYTHONPATH=src python3 examples/pipeline_integration.py \\
        --query "mindfulness depression" --max_papers 3
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# 添加路径
CYBERNETICS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CYBERNETICS_ROOT / "src"))

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.adapters import NativeAdapter
from cybernetics_agent.core.base import CyberneticsEvent, EventType


class PipelineCyberneticsIntegration:
    """
    Pipeline 与控制论层的集成器。
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        # 加载或创建配置
        if config_path and Path(config_path).exists():
            self.config = CyberneticsConfig.from_json(config_path)
        else:
            self.config = CyberneticsConfig(
                project_name="demo-pipeline",
                feedback_loop={
                    "enabled": True,
                    "mode": "automatic",
                    "actions": [
                        {"trigger": "tool_error_rate > 0.3", "action": "retry"},
                        {"trigger": "stage_failure_rate > 0.5", "action": "degrade"},
                    ],
                    "max_feedback_depth": 3,
                },
                stability={"enabled": True},
                system_id={"enabled": True},
                optimal_control={
                    "enabled": True,
                    "budgets": {
                        "tokens_per_session": 50000,
                        "api_calls_per_session": 20,
                        "cost_usd_per_session": 2.0,
                    },
                },
                info_flow={"enabled": True, "filters": []},
                adaptive={"enabled": True},
                hierarchy={"enabled": True},
            )

        # 创建上下文
        self.ctx = CyberneticsContext(self.config)
        self.adapter = NativeAdapter(self.ctx)
        self.adapter.install(None)

        # 统计
        self._stage_times: Dict[str, float] = {}

    def _emit_stage_start(self, stage: str, details: Optional[Dict] = None) -> None:
        """发射阶段开始事件。"""
        self._stage_times[stage] = time.time()
        self.ctx.emit(CyberneticsEvent.create(
            EventType.STAGE_TRANSITION,
            self.ctx.session_id,
            {"stage": stage, "status": "started", "details": details or {}},
        ))

    def _emit_stage_end(self, stage: str, success: bool = True, extra: Optional[Dict] = None) -> None:
        """发射阶段结束事件。"""
        duration = time.time() - self._stage_times.get(stage, time.time())
        payload = {
            "stage": stage,
            "status": "completed" if success else "failed",
            "duration": duration,
            "success": success,
        }
        if extra:
            payload.update(extra)
        self.ctx.emit(CyberneticsEvent.create(
            EventType.STAGE_TRANSITION,
            self.ctx.session_id,
            payload,
        ))

    def run_pipeline(self, query: str, max_papers: int = 3) -> Dict[str, Any]:
        """
        运行 Pipeline 并插入控制论层。

        这是一个简化的集成示例，演示如何用控制论层监控 pipeline。
        """
        results: Dict[str, Any] = {
            "query": query,
            "max_papers": max_papers,
            "stages": {},
        }

        # 阶段 1: 搜索
        self._emit_stage_start("search", {"query": query, "max_papers": max_papers})
        papers = []
        try:
            import asyncio
            from search_orchestrator import SearchOrchestrator

            async def do_search():
                async with SearchOrchestrator() as searcher:
                    return await searcher.search(query, max_results=max_papers)

            papers = asyncio.run(do_search())
            results["stages"]["search"] = {"found": len(papers), "papers": papers}
            self._emit_stage_end("search", success=True, extra={"found": len(papers)})
        except Exception as e:
            self._emit_stage_end("search", success=False, extra={"error": str(e)})
            results["stages"]["search"] = {"error": str(e)}
            papers = []  # 确保后续有初始值

        # 阶段 2: 下载
        self._emit_stage_start("download")
        try:
            from download_manager import DownloadManager
            dm = DownloadManager()
            downloaded = []
            for paper in papers:
                result = dm.download(paper)
                downloaded.append(result)
            results["stages"]["download"] = {"downloaded": len(downloaded)}
            self._emit_stage_end("download", success=True, extra={"count": len(downloaded)})
        except Exception as e:
            self._emit_stage_end("download", success=False, extra={"error": str(e)})
            results["stages"]["download"] = {"error": str(e)}

        # 阶段 3: 生成报告
        self._emit_stage_start("generate", {"branch": "review"})
        try:
            from branch_a_review_generator import ReviewGenerator
            gen = ReviewGenerator()
            # 尝试多种调用方式
            report = None
            try:
                report = gen.generate(query=query, papers=papers)
            except TypeError:
                try:
                    report = gen.generate(papers=papers)
                except TypeError:
                    report = gen.generate(query)
            results["stages"]["generate"] = {"report_length": len(str(report)) if report else 0}
            self._emit_stage_end("generate", success=True)
        except Exception as e:
            self._emit_stage_end("generate", success=False, extra={"error": str(e)})
            results["stages"]["generate"] = {"error": str(e)}

        # 收集统计
        results["cybernetics_status"] = self.ctx.get_status()
        results["conversion_funnel"] = self._get_conversion_funnel()
        self.ctx.shutdown()

        return results

    def _get_conversion_funnel(self) -> Dict[str, float]:
        """获取转化漏斗。"""
        si = self.ctx.get_module("system_id")
        if si:
            return si.get_conversion_funnel(["search", "download", "generate"])
        return {}

    def print_report(self, results: Dict[str, Any]) -> None:
        """打印运行报告。"""
        print("\n" + "=" * 60)
        print("🐙 Cybernetics Pipeline 运行报告")
        print("=" * 60)

        print(f"\n查询: {results['query']}")
        print(f"最大论文数: {results['max_papers']}")

        print("\n┌────────────────────────────────────────────────┐")
        print("│ 阶段状态                                         │")
        print("├────────────────────────────────────────────────┤")

        for stage_name, stage_data in results["stages"].items():
            if "error" in stage_data:
                icon = "❌"
                detail = f"失败: {stage_data['error'][:50]}"
            else:
                icon = "✅"
                detail = json.dumps(stage_data, ensure_ascii=False)[:50]
            print(f"│ {icon} {stage_name:15s} {detail:36s} │")

        print("└────────────────────────────────────────────────┘")

        # 转化漏斗
        funnel = results.get("conversion_funnel", {})
        if funnel:
            print("\n┼ 转化漏斗")
            for key, rate in funnel.items():
                bar = "█" * int(rate * 20)
                print(f"  {key:25s} {rate:.1%} {bar}")

        # 控制论状态
        status = results.get("cybernetics_status", {})
        if "modules" in status:
            print("\n┼ 控制论模块状态")
            for mod_name, mod_status in status["modules"].items():
                enabled = "✅" if mod_status.get("enabled") else "❌"
                print(f"  {enabled} {mod_name}")

        print("\n" + "=" * 60)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Cybernetics Pipeline Integration Demo")
    parser.add_argument("--query", default="mindfulness depression", help="搜索查询")
    parser.add_argument("--max_papers", type=int, default=3, help="最大论文数")
    parser.add_argument("--config", help="控制论配置文件路径")
    args = parser.parse_args()

    print(f"🐙 启动 Cybernetics Pipeline 集成测试")
    print(f"   查询: {args.query}")
    print(f"   最大论文数: {args.max_papers}")
    print()

    integration = PipelineCyberneticsIntegration(config_path=args.config)
    results = integration.run_pipeline(args.query, args.max_papers)
    integration.print_report(results)

    # 保存结果
    output_path = Path("pipeline_cybernetics_report.json")
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    print(f"\n📄️ 详细报告已保存至: {output_path}")


if __name__ == "__main__":
    main()
