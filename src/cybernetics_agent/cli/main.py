"""
CLI 入口。

提供 cybernetix 命令行工具。
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, List, Optional


DESCRIPTION = """
Cybernetics Agent CLI

控制论 Agent 增强层的命令行工具。

常用命令:
    cybernetix init              初始化配置文件
    cybernetix audit <path>      审计代码目录
    cybernetix report            生成审计报告
    cybernetix dashboard         启动 Web 仪表盘
    cybernetix validate <file>   验证配置文件
"""


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="cybernetix",
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init
    init_parser = subparsers.add_parser("init", help="初始化配置文件")
    init_parser.add_argument(
        "-o", "--output",
        default="cybernetics.json",
        help="输出文件路径 (默认: cybernetics.json)",
    )
    init_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="强制覆盖已存在的配置文件",
    )
    init_parser.add_argument(
        "--format",
        choices=["json", "yaml"],
        default="json",
        help="配置文件格式",
    )

    # audit
    audit_parser = subparsers.add_parser("audit", help="审计代码目录")
    audit_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="要审计的代码路径 (默认: 当前目录)",
    )
    audit_parser.add_argument(
        "-o", "--output",
        help="输出报告文件路径",
    )
    audit_parser.add_argument(
        "-f", "--format",
        choices=["json", "markdown", "html"],
        default="markdown",
        help="报告格式",
    )
    audit_parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        default=True,
        help="递归审计子目录",
    )

    # report
    report_parser = subparsers.add_parser("report", help="生成审计报告")
    report_parser.add_argument(
        "-i", "--input",
        help="审计结果文件路径",
    )
    report_parser.add_argument(
        "-o", "--output",
        default="cybernetics_report.md",
        help="输出报告路径",
    )
    report_parser.add_argument(
        "-f", "--format",
        choices=["markdown", "html", "json"],
        default="markdown",
        help="报告格式",
    )

    # dashboard
    dashboard_parser = subparsers.add_parser("dashboard", help="启动 Web 仪表盘")
    dashboard_parser.add_argument(
        "-p", "--port",
        type=int,
        default=8080,
        help="监听端口 (默认: 8080)",
    )
    dashboard_parser.add_argument(
        "-H", "--host",
        default="127.0.0.1",
        help="监听地址 (默认: 127.0.0.1)",
    )
    dashboard_parser.add_argument(
        "-c", "--config",
        default="cybernetics.json",
        help="配置文件路径",
    )

    # validate
    validate_parser = subparsers.add_parser("validate", help="验证配置文件")
    validate_parser.add_argument(
        "file",
        nargs="?",
        default="cybernetics.json",
        help="配置文件路径 (默认: cybernetics.json)",
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    CLI 入口函数。
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 1

    command = parsed.command

    if command == "init":
        from .init import run_init
        return run_init(parsed)

    elif command == "audit":
        from .audit import run_audit
        return run_audit(parsed)

    elif command == "report":
        from .report import run_report
        return run_report(parsed)

    elif command == "dashboard":
        from .dashboard import run_dashboard
        return run_dashboard(parsed)

    elif command == "validate":
        from .validate import run_validate
        return run_validate(parsed)

    else:
        parser.print_help()
        return 1
