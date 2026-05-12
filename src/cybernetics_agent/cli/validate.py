"""
validate 命令。

验证控制论配置文件的合法性。
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigValidator:
    """配置文件验证器。"""

    REQUIRED_VERSION = "1.0"
    VALID_BACKENDS = ["jsonl", "sqlite", "redis"]

    def __init__(self) -> None:
        self._errors: List[str] = []
        self._warnings: List[str] = []

    def validate(self, config: Dict[str, Any]) -> bool:
        """验证配置。

        返回 True 表示验证通过。
        """
        self._errors.clear()
        self._warnings.clear()

        # 检查版本
        version = config.get("version")
        if not version:
            self._errors.append("缺少 'version' 字段")
        elif version != self.REQUIRED_VERSION:
            self._warnings.append(f"版本 {version} 不是推荐版本 {self.REQUIRED_VERSION}")

        # 检查项目名
        if not config.get("project_name"):
            self._warnings.append("未设置 'project_name'")

        # 检查每个模块
        modules = [
            "feedback_loop",
            "stability",
            "system_id",
            "optimal_control",
            "info_flow",
            "adaptive",
            "hierarchy",
        ]

        for module_name in modules:
            module_config = config.get(module_name)
            if module_config is None:
                self._warnings.append(f"模块 '{module_name}' 未配置，将使用默认值")
            elif not isinstance(module_config, dict):
                self._errors.append(f"模块 '{module_name}' 必须是字典类型")
            elif "enabled" not in module_config:
                self._warnings.append(f"模块 '{module_name}' 缺少 'enabled' 字段")

        # 检查存储配置
        storage = config.get("storage", {})
        if storage:
            backend = storage.get("backend")
            if backend and backend not in self.VALID_BACKENDS:
                self._errors.append(f"不支持的存储后端: {backend}")

        # 检查 feedback_loop 规则
        fb_config = config.get("feedback_loop", {})
        if fb_config and fb_config.get("enabled"):
            actions = fb_config.get("actions", [])
            for i, action in enumerate(actions):
                if "trigger" not in action:
                    self._errors.append(f"feedback_loop.actions[{i}] 缺少 'trigger'")
                if "action" not in action:
                    self._errors.append(f"feedback_loop.actions[{i}] 缺少 'action'")

        # 检查 stability 配置
        st_config = config.get("stability", {})
        if st_config and st_config.get("enabled"):
            retry = st_config.get("retry", {})
            max_retries = retry.get("max_retries", 3)
            if not isinstance(max_retries, int) or max_retries < 0:
                self._errors.append("stability.retry.max_retries 必须是非负整数")

            backoff = retry.get("backoff", "exponential")
            if backoff not in ["exponential", "linear", "fixed"]:
                self._errors.append(f"stability.retry.backoff 不支持的值: {backoff}")

        return len(self._errors) == 0

    def get_errors(self) -> List[str]:
        return list(self._errors)

    def get_warnings(self) -> List[str]:
        return list(self._warnings)


def run_validate(args: Namespace) -> int:
    """执行 validate 命令。"""
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return 1

    print(f"🔍 正在验证: {file_path}")
    print()

    # 加载配置
    try:
        if file_path.suffix == ".json":
            config = json.loads(file_path.read_text(encoding="utf-8"))
        elif file_path.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                config = yaml.safe_load(file_path.read_text(encoding="utf-8"))
            except ImportError:
                print("❌ 需要安装 pyyaml: pip install pyyaml")
                return 1
        else:
            print(f"❌ 不支持的文件格式: {file_path.suffix}")
            return 1
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return 1
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return 1

    # 验证
    validator = ConfigValidator()
    is_valid = validator.validate(config)

    errors = validator.get_errors()
    warnings = validator.get_warnings()

    if errors:
        print(f"❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"   - {error}")
        print()

    if warnings:
        print(f"⚠️  发现 {len(warnings)} 个警告:")
        for warning in warnings:
            print(f"   - {warning}")
        print()

    if is_valid and not warnings:
        print("✅ 配置文件验证通过！")
        return 0
    elif is_valid:
        print("✅ 配置文件有效，但有警告建议处理")
        return 0
    else:
        print("❌ 配置文件验证失败")
        return 1

