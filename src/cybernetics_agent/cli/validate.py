"""
validate 命令。

验证控制论配置文件的合法性。复用 CyberneticsConfig.validate() 提供友好错误。
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from ..config import CyberneticsConfig


class ConfigValidator:
    """配置文件验证器—复用核心配置对象的验证逻辑。"""

    VALID_BACKENDS = ["jsonl", "sqlite", "redis"]

    def __init__(self) -> None:
        self._errors: list[str] = []
        self._warnings: list[str] = []

    def validate(self, config: dict[str, Any]) -> bool:
        """验证配置。

        返回 True 表示验证通过。
        """
        self._errors.clear()
        self._warnings.clear()

        # 使用核心配置类的 schema 验证
        try:
            cfg = CyberneticsConfig.from_dict(config)
            schema_errors = cfg.validate()
            self._errors.extend(schema_errors)
        except Exception as e:
            self._errors.append(f"配置格式错误: {e}")
            return False

        # 额外的后端与存储验证
        storage = config.get("storage", {})
        if storage:
            backend = storage.get("backend")
            if backend and backend not in self.VALID_BACKENDS:
                self._errors.append(f"不支持的存储后端: {backend}")

        # 检查 feedback_loop actions 类型
        fb = config.get("feedback_loop", {})
        if fb and fb.get("enabled"):
            actions = fb.get("actions", [])
            if actions and not all(isinstance(a, str) for a in actions):
                self._errors.append("feedback_loop.actions 必须是字符串列表")

        # 检查 stability retry backoff 值
        st = config.get("stability", {})
        if st and st.get("enabled"):
            retry = st.get("retry", {})
            backoff = retry.get("backoff", "exponential")
            if backoff not in ("exponential", "linear", "fixed"):
                self._errors.append(f"stability.retry.backoff 不支持的值: {backoff}")

        return len(self._errors) == 0

    def get_errors(self) -> list[str]:
        return list(self._errors)

    def get_warnings(self) -> list[str]:
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
            config: dict[str, Any] = json.loads(file_path.read_text(encoding="utf-8"))
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
