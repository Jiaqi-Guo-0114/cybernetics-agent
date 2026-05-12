"""
框架适配器。

支持的框架:
- Native (纯 Python)
- LangChain
- AutoGen
- CrewAI
- Hermes
- Claude Code
- Codex
- OpenClaw
- Qwenpaw
"""

from .autogen import AutoGenAdapter
from .base import BaseAdapter
from .claude_code import ClaudeCodeAdapter
from .codex import CodexAdapter
from .crewai import CrewAIAdapter
from .hermes import HermesAdapter
from .langchain import LangChainAdapter
from .native import NativeAdapter
from .openclaw import OpenClawAdapter
from .qwenpaw import QwenpawAdapter

__all__ = [
    "BaseAdapter",
    "NativeAdapter",
    "LangChainAdapter",
    "AutoGenAdapter",
    "CrewAIAdapter",
    "HermesAdapter",
    "ClaudeCodeAdapter",
    "CodexAdapter",
    "OpenClawAdapter",
    "QwenpawAdapter",
]
