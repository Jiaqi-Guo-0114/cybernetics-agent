"""

plugin 命令处理。

插件发现、列表和管理。
"""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from ..runtime.plugin_loader import PluginLoader


def run_plugin(args: Namespace) -> int:
    """处理 plugin 命令。"""
    subcommand = getattr(args, "plugin_command", None)
    plugin_dir = Path(args.dir)

    if subcommand == "list" or subcommand is None:
        return _run_list(plugin_dir)
    elif subcommand == "discover":
        return _run_discover(plugin_dir)
    else:
        print(f"未知的插件命令: {subcommand}")
        return 1


def _run_list(plugin_dir: Path) -> int:
    """列出已加载的插件。"""
    print(f"插件目录: {plugin_dir}")
    print()

    if not plugin_dir.exists():
        print("插件目录不存在，尚未加载任何插件。")
        return 0

    loader = PluginLoader()
    plugins = loader.discover(plugin_dir)

    if not plugins:
        print("未发现任何插件。")
        return 0

    print(f"发现 {len(plugins)} 个插件:")
    print()
    for p in plugins:
        loaded = "✅ 已加载" if loader.is_loaded(p.name) else "○ 未加载"
        print(f"  {p.name:30s} {loaded:12s}  {p.source_file.name}")
        if p.description:
            desc = p.description.strip().split("\n")[0][:60]
            print(f"    {desc}")
    return 0


def _run_discover(plugin_dir: Path) -> int:
    """发现插件目录中的所有插件。"""
    print(f"扫描插件目录: {plugin_dir}")
    print()

    if not plugin_dir.exists():
        print("插件目录不存在。")
        print(f"可以创建: mkdir -p {plugin_dir}")
        return 1

    loader = PluginLoader()
    plugins = loader.discover(plugin_dir)

    if not plugins:
        print("未发现任何插件。")
        print("确保 .py 文件中定义了继承 ICyberneticsModule 的类。")
        return 0

    print(f"发现 {len(plugins)} 个插件:")
    print()
    for p in plugins:
        print(f"  名称: {p.name}")
        print(f"  文件: {p.source_file}")
        print(f"  类:   {p.module_class.__name__}")
        if p.description:
            print(f"  描述: {p.description.strip().split(chr(10))[0][:80]}")
        print()

    return 0
