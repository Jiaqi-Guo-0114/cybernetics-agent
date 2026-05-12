"""
audit 命令。

检测代码中的控制论缺陷。
"""

from __future__ import annotations

import ast
import json
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditRule:
    """单条审计规则。"""

    def __init__(
        self,
        rule_id: str,
        description: str,
        severity: str,  # "error" | "warning" | "info"
        check_func: Any,
    ) -> None:
        self.rule_id = rule_id
        self.description = description
        self.severity = severity
        self.check_func = check_func


class CodeAuditor:
    """代码审计器。

    扫描 Python 代码，检测控制论缺陷。
    """

    RULES: List[AuditRule] = []

    def __init__(self) -> None:
        self._findings: List[Dict[str, Any]] = []
        self._rules = self._build_rules()

    def _build_rules(self) -> List[AuditRule]:
        """构建审计规则列表。"""
        rules = [
            AuditRule(
                "CYB001",
                "缺少错误处理（未封装 try/except）",
                "warning",
                self._check_error_handling,
            ),
            AuditRule(
                "CYB002",
                "硬编码超时值（未使用配置化超时）",
                "warning",
                self._check_hardcoded_timeout,
            ),
            AuditRule(
                "CYB003",
                "缺少重试机制（直接调用外部 API 无重试）",
                "error",
                self._check_missing_retry,
            ),
            AuditRule(
                "CYB004",
                "缺少日志/指标采集（关键流程无日志记录）",
                "info",
                self._check_missing_logging,
            ),
            AuditRule(
                "CYB005",
                "未实现故障降级（崩溃后无后备方案）",
                "error",
                self._check_missing_fallback,
            ),
            AuditRule(
                "CYB006",
                "硬编码 API key/秘钥（安全风险）",
                "error",
                self._check_hardcoded_secrets,
            ),
            AuditRule(
                "CYB007",
                "缺少分层控制（所有决策在同一层级）",
                "info",
                self._check_flat_decisions,
            ),
        ]
        return rules

    def audit_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """审计单个文件。"""
        findings = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError:
            return findings
        except Exception:
            return findings

        for rule in self._rules:
            result = rule.check_func(tree, source, file_path)
            if result:
                for finding in result:
                    finding["rule_id"] = rule.rule_id
                    finding["description"] = rule.description
                    finding["severity"] = rule.severity
                    finding["file"] = str(file_path)
                    findings.append(finding)

        return findings

    def audit_directory(self, path: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """审计目录。"""
        all_findings = []

        if recursive:
            files = list(path.rglob("*.py"))
        else:
            files = list(path.glob("*.py"))

        for file_path in files:
            findings = self.audit_file(file_path)
            all_findings.extend(findings)

        return all_findings

    # ── 规则实现 ──

    def _check_error_handling(self, tree: ast.AST, source: str, path: Path) -> List[Dict[str, Any]]:
        """检查是否缺少错误处理。"""
        findings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_try = any(
                    isinstance(child, ast.Try) for child in ast.walk(node)
                )
                # 只检查简单情况：包含网络/文件/外部调用的函数
                body_str = ast.dump(node)
                if (
                    "requests" in body_str
                    or "open(" in body_str
                    or "urlopen" in body_str
                    or "Client" in body_str
                ) and not has_try:
                    findings.append({
                        "line": node.lineno,
                        "function": node.name,
                        "message": f"函数 '{node.name}' 包含外部调用但缺少 try/except",
                    })
        return findings

    def _check_hardcoded_timeout(self, tree: ast.AST, source: str, path: Path) -> List[Dict[str, Any]]:
        """检查硬编码超时值。"""
        findings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)) and node.value in [30, 60, 120, 300]:
                    # 检查上下文是否是 timeout 参数
                    line = source.split("\n")[node.lineno - 1]
                    if "timeout" in line.lower() or "time" in line.lower():
                        findings.append({
                            "line": node.lineno,
                            "message": f"发现硬编码超时值: {node.value}，建议使用配置化超时",
                        })
        return findings

    def _check_missing_retry(self, tree: ast.AST, source: str, path: Path) -> List[Dict[str, Any]]:
        """检查缺少重试机制。"""
        findings = []
        source_lower = source.lower()
        has_retry = "retry" in source_lower or "backoff" in source_lower or "attempt" in source_lower

        # 检查是否有外部 API 调用
        has_api_call = (
            "requests." in source
            or "httpx." in source
            or "urllib" in source
            or "openai" in source_lower
            or "anthropic" in source_lower
        )

        if has_api_call and not has_retry:
            findings.append({
                "line": 1,
                "message": "文件包含外部 API 调用但未发现重试机制",
            })
        return findings

    def _check_missing_logging(self, tree: ast.AST, source: str, path: Path) -> List[Dict[str, Any]]:
        """检查缺少日志采集。"""
        findings = []
        has_logging = "import logging" in source or "from logging" in source
        has_print = "print(" in source

        if not has_logging and has_print:
            findings.append({
                "line": 1,
                "message": "使用 print() 而非 logging 模块，建议使用结构化日志",
            })
        return findings

    def _check_missing_fallback(self, tree: ast.AST, source: str, path: Path) -> List[Dict[str, Any]]:
        """检查缺少故障降级。"""
        findings = []
        has_fallback = (
            "fallback" in source.lower()
            or "degrade" in source.lower()
            or "backup" in source.lower()
        )
        has_api_call = (
            "requests." in source
            or "httpx." in source
        )

        if has_api_call and not has_fallback:
            findings.append({
                "line": 1,
                "message": "包含网络调用但未发现故障降级机制",
            })
        return findings

    def _check_hardcoded_secrets(self, tree: ast.AST, source: str, path: Path) -> List[Dict[str, Any]]:
        """检查硬编码的秘钥。"""
        findings = []
        secret_patterns = [
            ("sk-", "OpenAI API key"),
            ("api_key", "API key"),
            ("secret", "secret"),
            ("password", "password"),
            ("token", "token"),
        ]

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value
                for pattern, name in secret_patterns:
                    if pattern in value and len(value) > 20:
                        findings.append({
                            "line": node.lineno,
                            "message": f"可能存在硬编码 {name}，建议使用环境变量或密钥管理器",
                        })
                        break
        return findings

    def _check_flat_decisions(self, tree: ast.AST, source: str, path: Path) -> List[Dict[str, Any]]:
        """检查是否有分层控制。"""
        findings = []
        # 简化检查：查找是否有明确的层级区分
        has_layer = (
            "strategic" in source.lower()
            or "tactical" in source.lower()
            or "executive" in source.lower()
            or "hierarchy" in source.lower()
        )

        # 检查是否是 Agent 类的核心文件
        if "agent" in str(path).lower() and not has_layer:
            findings.append({
                "line": 1,
                "message": "Agent 核心逻辑未发现分层控制结构，建议引入战略/战术/执行三层架构",
            })
        return findings


def run_audit(args: Namespace) -> int:
    """执行 audit 命令。"""
    target_path = Path(args.path)

    if not target_path.exists():
        print(f"❌ 路径不存在: {target_path}")
        return 1

    print(f"🔍 正在审计: {target_path}")
    print()

    auditor = CodeAuditor()

    if target_path.is_file():
        findings = auditor.audit_file(target_path)
    else:
        findings = auditor.audit_directory(target_path, recursive=args.recursive)

    # 统计
    severity_counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        severity_counts[f["severity"]] += 1

    # 输出结果
    if not findings:
        print("✅ 未发现问题！")
        return 0

    print(f"发现 {len(findings)} 个问题:")
    print(f"   错误: {severity_counts['error']}")
    print(f"   警告: {severity_counts['warning']}")
    print(f"   信息: {severity_counts['info']}")
    print()

    for finding in findings:
        severity_icon = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
        }.get(finding["severity"], "•")

        print(f"{severity_icon}  [{finding['rule_id']}] {finding['description']}")
        print(f"   文件: {finding['file']}:{finding.get('line', '?')}")
        print(f"   详情: {finding['message']}")
        print()

    # 保存报告
    if args.output:
        report = {
            "summary": {
                "total": len(findings),
                **severity_counts,
            },
            "findings": findings,
        }

        output_path = Path(args.output)
        if args.format == "json":
            output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        elif args.format == "markdown":
            md = _generate_markdown_report(report)
            output_path.write_text(md, encoding="utf-8")

        print(f"📄️ 报告已保存至: {output_path}")

    return 1 if severity_counts["error"] > 0 else 0


def _generate_markdown_report(report: Dict[str, Any]) -> str:
    """生成 Markdown 格式的审计报告。"""
    lines = [
        "# 控制论审计报告",
        "",
        "## 概览",
        "",
        f"- 总问题数: {report['summary']['total']}",
        f"- 错误: {report['summary']['error']}",
        f"- 警告: {report['summary']['warning']}",
        f"- 信息: {report['summary']['info']}",
        "",
        "## 详细发现",
        "",
    ]

    for finding in report["findings"]:
        severity = finding["severity"]
        lines.append(f"### [{finding['rule_id']}] {finding['description']}")
        lines.append("")
        lines.append(f"- **严重性**: {severity}")
        lines.append(f"- **文件**: `{finding['file']}:{finding.get('line', '?')}`")
        lines.append(f"- **说明**: {finding['message']}")
        lines.append("")

    return "\n".join(lines)
