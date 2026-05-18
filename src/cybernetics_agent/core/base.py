"""
控制论核心模块的抽象基类和事件系统。

所有七大原则模块必须继承 ICyberneticsModule。
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..context import CyberneticsContext


class EventType(Enum):
    """控制论事件类型。"""
    # Agent 生命周期
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"

    # 工具调用
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_ERROR = "tool_error"

    # LLM 交互
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    LLM_ERROR = "llm_error"

    # 用户交互
    USER_INPUT = "user_input"
    USER_FEEDBACK = "user_feedback"

    # 系统
    STAGE_TRANSITION = "stage_transition"
    ERROR = "error"
    RECOVERY = "recovery"
    DEGRADATION = "degradation"

    # 自定义
    CUSTOM = "custom"


@dataclass
class CyberneticsEvent:
    """
    控制论事件对象。

    所有模块之间的通信都通过事件进行。
    """
    event_type: EventType
    timestamp: float
    session_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])

    @classmethod
    def create(
        cls,
        event_type: EventType | str,
        session_id: str,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CyberneticsEvent:
        """便捷构造方法。

        event_type 支持 EventType 枚举或字符串（字符串会尝试匹配枚举，匹配失败则使用 CUSTOM）。
        """
        if isinstance(event_type, str):
            try:
                event_type = EventType(event_type)
            except ValueError:
                event_type = EventType.CUSTOM
        return cls(
            event_type=event_type,
            timestamp=time.time(),
            session_id=session_id,
            payload=payload or {},
            metadata=metadata or {},
        )


class ICyberneticsModule(ABC):
    """
    控制论模块基类。

    模块是“装饰器”——它们不替代业务逻辑，
    只是在关键节点插入控制逻辑。

    使用模式:
        >>> class MyModule(ICyberneticsModule):
        ...     name = "my_module"
        ...     def on_event(self, event):
        ...         if event.event_type == EventType.TOOL_ERROR:
        ...             return self._handle_error(event)
        ...         return event
        ...     def get_status(self):
        ...         return {"active": True}
    """

    name: str = ""
    enabled: bool = True

    def __init__(self, config: dict[str, Any], ctx: CyberneticsContext) -> None:
        self.config = config
        self.ctx = ctx
        self._initialized = False

    def initialize(self) -> None:
        """初始化模块。可重载以执行启动时逻辑。"""
        self._initialized = True

    def shutdown(self) -> None:
        """关闭模块。可重载以执行清理逻辑。"""
        self._initialized = False

    @abstractmethod
    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent | None:
        """
        处理事件。

        参数:
            event: 收到的事件

        返回:
            None — 事件被消耗，不再传播
            CyberneticsEvent — 修改后的事件，继续传播
        """
        ...

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """
        返回模块当前状态。

        用于审计报告和 Dashboard 展示。
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} enabled={self.enabled}>"
