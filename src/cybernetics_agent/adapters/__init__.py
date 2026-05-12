"""框架适配器。"""

from .autogen import AutoGenAdapter
from .base import BaseAdapter
from .crewai import CrewAIAdapter
from .hermes import HermesAdapter
from .langchain import LangChainAdapter
from .native import NativeAdapter

__all__ = [
    "BaseAdapter",
    "NativeAdapter",
    "LangChainAdapter",
    "AutoGenAdapter",
    "CrewAIAdapter",
    "HermesAdapter",
]
