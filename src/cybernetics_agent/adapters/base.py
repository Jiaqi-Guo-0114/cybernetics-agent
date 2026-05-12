"""
适配器基类。

所有框架适配器必须继承此基类。
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..core.base import CyberneticsEvent, EventType
    from ..context import CyberneticsContext


class BaseAdapter(ABC):
    """
    控制论框架适配器基类。

    子类必须实现 install 和 uninstall 方法，
    将控制论层插入到目标框架中。

    使用示例:
        >>> adapter = HermesAdapter(ctx)
        >>> adapter.install(hermes_plugin_context)
        >>> # ... 运行 ...
        >>> adapter.uninstall()
    """

    def __init__(self, ctx: "CyberneticsContext") -> None:
        self.ctx = ctx
        self._installed = False

    @abstractmethod
    def install(self, target: Any) -> None:
        """
        将控制论层安装到目标框架上。

        参数:
            target: 目标框架的特定对象（如 Hermes 的 PluginContext、
                   LangChain 的 LLM 实例等）
        """
        ...

    @abstractmethod
    def uninstall(self) -> None:
        """卸载控制论层，恢复目标框架的原始状态。"""
        ...

    def emit(
        self,
        event_type: "EventType",
        payload: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> None:
        """
        便捷方法：创建并发射事件。

        参数:
            event_type: 事件类型
            payload: 事件载荷
            session_id: session ID，为 None 时使用当前上下文的 session_id
        """
        from ..core.base import CyberneticsEvent

        evt = CyberneticsEvent.create(
            event_type=event_type,
            session_id=session_id or self.ctx.session_id,
            payload=payload,
        )
        self.ctx.emit(evt)

    def is_installed(self) -> bool:
        """检查是否已安装。"""
        return self._installed

    def __enter__(self) -> "BaseAdapter":
        """上下文管理器支持。"""
        return self

    def __exit__(self, *args: Any) -> None:
        """退出时自动卸载。"""
        if self._installed:
            self.uninstall()


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/adapters", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext
    from core.base import EventType

    # 测试 1: 基类抽象方法
    ctx = CyberneticsContext(CyberneticsConfig())

    class DummyAdapter(BaseAdapter):
        def install(self, target):
            self._installed = True

        def uninstall(self):
            self._installed = False

    adapter = DummyAdapter(ctx)
    assert adapter.is_installed() is False

    adapter.install(None)
    assert adapter.is_installed() is True
    print("  ✅ 测试 1 通过：基类安装/卸载")

    # 测试 2: 上下文管理器
    with DummyAdapter(ctx) as a:
        a.install(None)
        assert a.is_installed() is True
    assert a.is_installed() is False
    print("  ✅ 测试 2 通过：上下文管理器")

    print("\n  ✅ 适配器基类所有冒烟测试通过！")
