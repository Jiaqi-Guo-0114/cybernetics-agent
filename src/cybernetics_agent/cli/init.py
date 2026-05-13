"""

init 命令。

生成默认的控制论配置文件。
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    "version": "1.0",
    "project_name": "my-agent",
    "feedback_loop": {
        "enabled": True,
        "mode": "automatic",
        "actions": ["retry", "degrade"],
        "max_feedback_depth": 3
    },
    "stability": {
        "enabled": True,
        "timeout": {"default": 30, "llm": 120, "download": 60, "tool": 30},
        "retry": {"max_retries": 3, "backoff": "exponential", "base_delay": 1.0, "max_delay": 60.0},
        "circuit_breaker": {"enabled": True, "failure_threshold": 5, "recovery_timeout": 60, "half_open_max_calls": 3},
        "graceful_degradation": {"enabled": True, "chain": ["fulltext", "abstract", "metadata"]},
        "parallel_competition": {"enabled": True, "groups": [], "timeout_seconds": 120}
    },
    "system_id": {
        "enabled": True,
        "metrics": ["conversion_rate", "latency", "error_rate", "token_usage"],
        "sampling_rate": 1.0,
        "retention_days": 30
    },
    "optimal_control": {
        "enabled": True,
        "budgets": {"tokens_per_session": 100000, "api_calls_per_session": 50, "cost_usd_per_session": 5.0},
        "constraints": {"max_concurrent_tools": 5, "max_llm_requests_per_minute": 10}
    },
    "info_flow": {"enabled": True, "filters": [], "channels": ["event_bus", "metrics", "storage"]},
    "adaptive": {
        "enabled": True,
        "learning_rate": 0.3,
        "parameters": [],
        "user_behavior": {"track_topics": True, "track_feedback": True, "topic_decay_half_life_days": 7}
    },
    "hierarchy": {
        "enabled": True,
        "layers": [
            {"name": "strategic", "decision_types": ["goal", "branch", "budget"]},
            {"name": "tactical", "decision_types": ["parameter", "resource", "schedule"]},
            {"name": "executive", "decision_types": ["tool", "retry", "error_recovery"]}
        ]
    },
    "storage": {"backend": "jsonl", "path": "./.cybernetics", "rotation": {"max_file_size_mb": 10, "max_files": 10}}
}


def run_init(args: Namespace) -> int:
    """执行 init 命令。"""
    output_path = Path(args.output)

    if output_path.exists() and not getattr(args, "force", False):
        print(f"⚠️  文件已存在: {output_path}")
        response = input("要覆盖吗？(y/N): ").strip().lower()
        if response != "y":
            print("已取消")
            return 0

    config = DEFAULT_CONFIG.copy()
    config["project_name"] = output_path.parent.name or "my-agent"

    if args.format == "json":
        content = json.dumps(config, indent=2, ensure_ascii=False)
        output_path.write_text(content + "\n", encoding="utf-8")
    elif args.format == "yaml":
        try:
            import yaml
            content = yaml.dump(config, default_flow_style=False, allow_unicode=True)
            output_path.write_text(content, encoding="utf-8")
        except ImportError:
            print("❌ 需要安装 pyyaml: pip install pyyaml")
            return 1

    print(f"✅ 已生成配置文件: {output_path}")
    print(f"   格式: {args.format}")
    print(f"   项目名: {config['project_name']}")
    return 0

