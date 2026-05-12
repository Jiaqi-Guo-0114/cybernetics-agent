"""
框架适配器。

支持 Hermes、LangChain、CrewAI、AutoGen、Native 等多个框架。
"""

from .base import BaseAdapter
from .hermes import HermesAdapter
from .langchain import LangChainAdapter
from .crewai import CrewAIAdapter
from .autogen import AutoGenAdapter
from .native import NativeAdapter

__all__ = [
    "BaseAdapter",
    "HermesAdapter",
    "LangChainAdapter",
    "CrewAIAdapter",
    "AutoGenAdapter",
    "NativeAdapter",
]
