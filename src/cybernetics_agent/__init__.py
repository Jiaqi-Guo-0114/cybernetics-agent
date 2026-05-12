"""
cybernetics-agent: 一个框架无关的控制论 Agent 增强层。

基于钱学森《工程控制论》七大核心原则：
1. 反馈闭环 (Feedback Loop)
2. 稳定性优先 (Stability First)
3. 系统辨识 (System Identification)
4. 最优控制 (Optimal Control)
5. 信息论 (Information Theory)
6. 自适应 (Adaptive Control)
7. 分层控制 (Hierarchical Control)

使用示例:
    >>> from cybernetics_agent import CyberneticsContext, CyberneticsConfig
    >>> config = CyberneticsConfig.from_json("cybernetics.json")
    >>> ctx = CyberneticsContext(config)
    >>> ctx.emit_tool_result(tool_name="search", result=["paper1", "paper2"])
"""

__version__ = "0.1.0"
__author__ = "Cybernetics Agent Contributors"

from .config import CyberneticsConfig
from .context import CyberneticsContext
from .core.base import ICyberneticsModule, EventType, CyberneticsEvent

__all__ = [
    "CyberneticsConfig",
    "CyberneticsContext",
    "ICyberneticsModule",
    "EventType",
    "CyberneticsEvent",
]
