"""

report 命令。

生成控制论审计报告。
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any


def run_report(args: Namespace) -> int:
    """执行 report 命令。"""
    # 加载审计结果
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ 输入文件不存在: {input_path}")
            return 1
        audit_data = json.loads(input_path.read_text(encoding="utf-8"))
    else:
        # 尝试从默认位置加载
        default_path = Path("cybernetics_audit.json")
        if default_path.exists():
            audit_data = json.loads(default_path.read_text(encoding="utf-8"))
        else:
            print("⚠️  未找到审计结果，请先运行: cybernetix audit")
            return 1

    # 生成报告
    if args.format == "markdown":
        content = _generate_markdown(audit_data)
    elif args.format == "html":
        content = _generate_html(audit_data)
    elif args.format == "json":
        content = json.dumps(audit_data, indent=2, ensure_ascii=False)
    else:
        content = _generate_markdown(audit_data)

    # 保存
    output_path = Path(args.output)
    output_path.write_text(content, encoding="utf-8")

    print(f"✅ 报告已生成: {output_path}")
    print(f"   格式: {args.format}")
    print(f"   问题总数: {audit_data['summary']['total']}")
    return 0


def _generate_markdown(data: dict[str, Any]) -> str:
    """生成 Markdown 报告。"""
    summary = data["summary"]
    findings = data["findings"]

    lines = [
        "# 🐙 Cybernetics Agent 审计报告",
        "",
        "## 括要",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 总问题数 | {summary['total']} |",
        f"| 错误 | {summary['error']} |",
        f"| 警告 | {summary['warning']} |",
        f"| 信息 | {summary['info']} |",
        "",
        "## 详细发现",
        "",
    ]

    severity_emojis = {
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }

    for i, finding in enumerate(findings, 1):
        emoji = severity_emojis.get(finding["severity"], "•")
        lines.append(f"### {i}. {emoji} {finding['description']}")
        lines.append("")
        lines.append(f"- **规则 ID**: `{finding['rule_id']}`")
        lines.append(f"- **严重性**: {finding['severity']}")
        lines.append(f"- **位置**: `{finding['file']}:{finding.get('line', '?')}`")
        lines.append(f"- **说明**: {finding['message']}")
        lines.append("")

    return "\n".join(lines)


def _generate_html(data: dict[str, Any]) -> str:
    """生成 HTML 报告。"""
    summary = data["summary"]
    findings = data["findings"]

    severity_colors = {
        "error": "#dc3545",
        "warning": "#ffc107",
        "info": "#0dcaf0",
    }

    findings_html = ""
    for i, finding in enumerate(findings, 1):
        color = severity_colors.get(finding["severity"], "#6c757d")
        findings_html += f"""
        <div class="finding">
            <h3>{i}. {finding['description']}</h3>
            <p><span class="badge" style="background-color: {color}">{finding['severity']}</span></p>
            <p><strong>规则 ID:</strong> {finding['rule_id']}</p>
            <p><strong>位置:</strong> {finding['file']}:{finding.get('line', '?')}</p>
            <p><strong>说明:</strong> {finding['message']}</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Cybernetics Agent 审计报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .finding {{ border-left: 4px solid #dee2e6; padding-left: 20px; margin-bottom: 30px; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 4px; color: white; font-size: 12px; }}
        h1 {{ color: #212529; }}
        h3 {{ color: #495057; margin-top: 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #dee2e6; padding: 12px; text-align: left; }}
        th {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <h1>🐙 Cybernetics Agent 审计报告</h1>
    <div class="summary">
        <h2>括要</h2>
        <table>
            <tr><th>指标</th><th>数值</th></tr>
            <tr><td>总问题数</td><td>{summary['total']}</td></tr>
            <tr><td>错误</td><td>{summary['error']}</td></tr>
            <tr><td>警告</td><td>{summary['warning']}</td></tr>
            <tr><td>信息</td><td>{summary['info']}</td></tr>
        </table>
    </div>
    <h2>详细发现</h2>
    {findings_html}
</body>
</html>"""

