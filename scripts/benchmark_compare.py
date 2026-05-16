#!/usr/bin/env python3
"""
性能回归比较脚本。

用于 CI 中对比 pytest-benchmark 基线结果。
如果某个测试的平均耗时增加超过阈值，返回非零退出码。

使用方式：
    python scripts/benchmark_compare.py .benchmarks/baseline.json benchmark-results.json --threshold 10

参数：
    baseline: 基线 JSON 文件路径
    current: 当前测试结果 JSON 文件路径
    --threshold: 性能下降阈值（百分比），默认 10
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_benchmark_data(path: str) -> dict:
    """加载 pytest-benchmark JSON 结果。"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_benchmarks(
    baseline: dict,
    current: dict,
    threshold: float = 10.0,
) -> list[str]:
    """
    比较两个 benchmark 结果，返回回归列表。

    参数:
        baseline: 基线结果
        current: 当前结果
        threshold: 性能下降阈值（百分比）

    返回:
        回归信息列表
    """
    regressions: list[str] = []

    baseline_map = {
        b["name"]: b["stats"]["mean"]
        for b in baseline.get("benchmarks", [])
    }
    current_map = {
        b["name"]: b["stats"]["mean"]
        for b in current.get("benchmarks", [])
    }

    for name, current_mean in current_map.items():
        if name not in baseline_map:
            continue

        baseline_mean = baseline_map[name]
        if baseline_mean == 0:
            continue

        # 计算增幅百分比
        increase_pct = ((current_mean - baseline_mean) / baseline_mean) * 100

        if increase_pct > threshold:
            regressions.append(
                f"{name}: {baseline_mean:.6f}s -> {current_mean:.6f}s "
                f"(+{increase_pct:.1f}%, threshold={threshold}%)"
            )
        elif increase_pct < -threshold:
            # 性能提升
            regressions.append(
                f"{name}: {baseline_mean:.6f}s -> {current_mean:.6f}s "
                f"({increase_pct:.1f}%, improved)"
            )

    return regressions


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare benchmark results")
    parser.add_argument("baseline", help="Baseline benchmark JSON file")
    parser.add_argument("current", help="Current benchmark JSON file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Performance regression threshold in percent (default: 10)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code if regressions found",
    )
    args = parser.parse_args()

    if not Path(args.baseline).exists():
        print(f"Error: Baseline file not found: {args.baseline}")
        return 1

    if not Path(args.current).exists():
        print(f"Error: Current file not found: {args.current}")
        return 1

    baseline_data = load_benchmark_data(args.baseline)
    current_data = load_benchmark_data(args.current)

    regressions = compare_benchmarks(baseline_data, current_data, args.threshold)

    if not regressions:
        print("No performance changes detected.")
        return 0

    print(f"Performance comparison (threshold={args.threshold}%):")
    print("-" * 60)

    has_regression = False
    for r in regressions:
        print(f"  {r}")
        if "+" in r.split(":")[-1]:
            has_regression = True

    if has_regression and args.strict:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
