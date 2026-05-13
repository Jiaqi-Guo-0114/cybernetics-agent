"""
audit 命令。

检测代码中的控制论缺陷。
"""

from __future__ import annotations

import ast
import json
from argparse import Namespace
from pathlib import Path
from typing import Any

RULES = [
    ("CYB001", "warning", "缺少错误处理"),
    ("CYB002", "warning", "硬编码超时值"),
    ("CYB003", "error", "缺少重试机制"),
    ("CYB004", "info", "缺少日志采集"),
    ("CYB005", "error", "未实现故障降级"),
    ("CYB006", "error", "硬编码 API key"),
    ("CYB007", "info", "缺少分层控制"),
]


def _scan(tree: ast.AST, source: str, path: Path) -> list[dict[str, Any]]:
    """扫描代码返回问题列表。"""
    findings = []
    src = source.lower()
    body = ast.dump(tree)

    # CYB001: 缺少错误处理
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            has_try = any(isinstance(c, ast.Try) for c in ast.walk(node))
            if any(x in body for x in ("requests", "open(", "urlopen", "Client")) and not has_try:
                findings.append({"rule": 0, "line": node.lineno, "msg": f"函数 '{node.name}' 包含外部调用但缺少 try/except"})

    # CYB002: 硬编码超时
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and node.value in (30, 60, 120, 300):
            line = source.split("\n")[node.lineno - 1]
            if "timeout" in line.lower():
                findings.append({"rule": 1, "line": node.lineno, "msg": f"硬编码超时值 {node.value}"})

    # CYB003: 缺少重试
    has_retry = any(w in src for w in ("retry", "backoff", "attempt"))
    has_api = any(w in source for w in ("requests.", "httpx.", "urllib", "openai"))
    if has_api and not has_retry:
        findings.append({"rule": 2, "line": 1, "msg": "包含外部 API 调用但未发现重试机制"})

    # CYB004: 缺少日志
    if "import logging" not in source and "print(" in source:
        findings.append({"rule": 3, "line": 1, "msg": "使用 print() 而非 logging"})

    # CYB005: 缺少降级
    has_fallback = any(w in src for w in ("fallback", "degrade", "backup"))
    if has_api and not has_fallback:
        findings.append({"rule": 4, "line": 1, "msg": "包含网络调用但未发现故障降级"})

    # CYB006: 硬编码密钥
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value
            if any(p in v for p in ("sk-", "api_key", "secret", "password", "token")) and len(v) > 20:
                findings.append({"rule": 5, "line": node.lineno, "msg": "可能存在硬编码密钥"})
                break

    # CYB007: 分层控制
    has_layer = any(w in src for w in ("strategic", "tactical", "executive", "hierarchy"))
    if "agent" in str(path).lower() and not has_layer:
        findings.append({"rule": 6, "line": 1, "msg": "Agent 核心未发现分层控制"})

    return findings


def run_audit(args: Namespace) -> int:
    """执行 audit 命令。"""
    target = Path(args.path)
    if not target.exists():
        print(f"❌ 路径不存在: {target}")
        return 1

    files = [target] if target.is_file() else list(target.rglob("*.py") if args.recursive else target.glob("*.py"))

    findings = []
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for r in _scan(tree, f.read_text(encoding="utf-8"), f):
            rid, sev, desc = RULES[r["rule"]]
            findings.append({"rule_id": rid, "severity": sev, "desc": desc, "file": str(f), "line": r["line"], "msg": r["msg"]})

    counts = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        counts[finding["severity"]] += 1

    if not findings:
        print("未发现问题！")
        return 0

    icons = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"发现 {len(findings)} 个问题: 错误={counts['error']} 警告={counts['warning']} 信息={counts['info']}\n")
    for finding in findings:
        print(f"{icons[finding['severity']]} [{finding['rule_id']}] {finding['desc']}")
        print(f"   {finding['file']}:{finding['line']} — {finding['msg']}\n")

    if args.output:
        report = {"summary": {"total": len(findings), **counts}, "findings": findings}
        Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"报告已保存: {args.output}")

    return 1 if counts["error"] > 0 else 0
