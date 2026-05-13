"""预设命令处理。"""


from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from ..config import CyberneticsConfig
from ..presets import apply_preset, describe_preset, get_preset, list_presets


def run_preset(args: Namespace) -> int:
    """处理 preset 命令。"""
    subcommand = getattr(args, "preset_command", None)

    if subcommand == "list" or subcommand is None:
        return _run_list()
    elif subcommand == "show":
        return _run_show(args)
    elif subcommand == "apply":
        return _run_apply(args)
    elif subcommand == "init":
        return _run_init(args)
    else:
        print(f"未知的预设命令: {subcommand}")
        return 1


def _run_list() -> int:
    """列出所有可用预设。"""
    names = list_presets()
    print("可用的策略预设:")
    print()
    for name in names:
        desc = describe_preset(name)
        print(f"  {name:20s}  {desc}")
    return 0


def _run_show(args: Namespace) -> int:
    """查看指定预设的详情。"""
    name = args.name
    try:
        preset = get_preset(name)
    except KeyError as e:
        print(f"错误: {e}")
        return 1

    print(f"预设: {name}")
    print(f"描述: {describe_preset(name)}")
    print()
    print(json.dumps(preset, indent=2, ensure_ascii=False))
    return 0


def _run_apply(args: Namespace) -> int:
    """将预设应用到现有配置文件。"""
    name = args.name
    config_path = Path(args.config)
    output_path = Path(args.output) if args.output else config_path

    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        return 1

    try:
        base = CyberneticsConfig.from_json(config_path)
        result = apply_preset(base, name)
    except KeyError as e:
        print(f"错误: {e}")
        return 1
    except Exception as e:
        print(f"加载配置失败: {e}")
        return 1

    # 验证结果
    errors = result.validate()
    if errors:
        print(f"警告: 合并后的配置存在 {len(errors)} 个问题:")
        for e in errors:
            print(f"  - {e}")
        print("仍然写入文件? 请确认。")
        # 生产环境可以在这里添加确认提示

    output_path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"已将预设 '{name}' 应用到 {output_path}")
    return 0


def _run_init(args: Namespace) -> int:
    """用预设初始化新配置文件。"""
    name = args.name
    output_path = Path(args.output)

    if output_path.exists():
        print(f"错误: 文件已存在: {output_path}")
        print("请先删除或使用 -f 覆盖。")
        return 1

    try:
        preset = get_preset(name)
    except KeyError as e:
        print(f"错误: {e}")
        return 1

    # 包装成完整的配置对象格式
    config = CyberneticsConfig.from_dict(preset)
    errors = config.validate()
    if errors:
        print(f"警告: 预设配置存在 {len(errors)} 个问题:")
        for e in errors:
            print(f"  - {e}")

    output_path.write_text(json.dumps(config.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"已用预设 '{name}' 创建 {output_path}")
    return 0
