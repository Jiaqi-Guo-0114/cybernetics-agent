"""
插件加载器。

支持动态发现、加载和卸载自定义控制论模块插件。
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

from ..core.base import ICyberneticsModule


class PluginInfo:
    """插件元信息。"""

    def __init__(
        self,
        name: str,
        module_class: type[ICyberneticsModule],
        source_file: Path,
        description: str = "",
    ) -> None:
        self.name = name
        self.module_class = module_class
        self.source_file = source_file
        self.description = description or module_class.__doc__ or ""

    def __repr__(self) -> str:
        return f"<PluginInfo {self.name} from {self.source_file.name}>"


class PluginLoader:
    """
    插件加载器。

    使用示例:
        >>> loader = PluginLoader()
        >>> plugins = loader.discover(Path("./plugins"))
        >>> for p in plugins:
        ...     print(p.name, p.module_class)
    """

    def __init__(self) -> None:
        self._loaded: dict[str, PluginInfo] = {}

    def discover(self, directory: Path) -> list[PluginInfo]:
        """
        扫描目录发现所有可用插件。

        Args:
            directory: 插件目录路径

        Returns:
            发现的插件信息列表
        """
        if not directory.exists() or not directory.is_dir():
            return []

        discovered: list[PluginInfo] = []
        for py_file in sorted(directory.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            plugins = self._inspect_file(py_file)
            discovered.extend(plugins)

        return discovered

    def _inspect_file(self, file_path: Path) -> list[PluginInfo]:
        """检查单个 Python 文件中的插件类。"""
        module_name = f"_cybernetics_plugin_{file_path.stem}"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            return []

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            return []

        plugins: list[PluginInfo] = []
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if obj is ICyberneticsModule:
                continue
            if issubclass(obj, ICyberneticsModule) and hasattr(obj, "name") and obj.name:
                plugins.append(PluginInfo(
                    name=obj.name,
                    module_class=obj,
                    source_file=file_path,
                    description=obj.__doc__ or "",
                ))

        return plugins

    def load(
        self,
        plugin_info: PluginInfo,
        config: dict[str, Any],
        ctx: Any,
    ) -> ICyberneticsModule | None:
        """
        加载单个插件并实例化。

        Args:
            plugin_info: 插件信息
            config: 插件配置
            ctx: CyberneticsContext

        Returns:
            实例化后的模块，或 None（加载失败时）
        """
        try:
            instance = plugin_info.module_class(config=config, ctx=ctx)
            self._loaded[plugin_info.name] = plugin_info
            return instance
        except Exception:
            return None

    def unload(self, name: str) -> bool:
        """卸载已加载的插件。"""
        if name in self._loaded:
            del self._loaded[name]
            return True
        return False

    def list_loaded(self) -> list[str]:
        """列出已加载的插件名称。"""
        return list(self._loaded.keys())

    def is_loaded(self, name: str) -> bool:
        """检查插件是否已加载。"""
        return name in self._loaded
