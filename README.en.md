# 🦙 Cybernetics Agent

> A framework-agnostic cybernetics enhancement layer for AI agents.
> Based on H.S. Tsien's *Engineering Cybernetics* seven core principles, enabling any Python agent with self-adaptive, self-healing, and self-optimizing capabilities.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-15%2F15-brightgreen.svg)]()

🌐 **[English](README.en.md)** · [中文](README.md) · [Français](README.fr.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

---

## ✅ Features

- **Framework-agnostic** — Pure standard library, zero external dependencies
- **Seven Principles** — Full coverage of Tsien's *Engineering Cybernetics*
- **Multi-framework adapters** — LangChain, AutoGen, CrewAI, Hermes, Claude Code, Codex, and more
- **Declarative config** — JSON/YAML configuration, flexible and controllable
- **Full CLI toolkit** — `cybernetix` command-line tools (init / audit / dashboard / run)
- **Thread-safe** — Built-in threading locks for safety

## 🚀 Quick Start

```bash
# Install
pip install cybernetics-agent

# Initialize config
cybernetix init

# Use
python -c "
from cybernetics_agent import CyberneticsConfig, CyberneticsContext
ctx = CyberneticsContext(CyberneticsConfig(project_name='my-agent'))
ctx.emit_tool_result('search', ['paper1', 'paper2'])
print(ctx.get_status())
"
```

## 🎯 Seven Principles

| Principle | Module | Function |
|-----------|--------|----------|
| 1. Feedback Loop | FeedbackLoop | Trigger-based actions, automatic adjustment |
| 2. Stability First | StabilityEngine | Retry, circuit breaker, degradation, timeout |
| 3. System Identification | SystemIdentifier | Conversion funnel, efficiency metrics |
| 4. Optimal Control | OptimalController | Budget management, constraint checking |
| 5. Information Theory | InfoFlow | Message filtering, distribution |
| 6. Adaptive Control | AdaptiveTuner | Parameter auto-tuning |
| 7. Hierarchical Control | HierarchyController | Strategic / Tactical / Executive layers |

## 🔧 Supported Frameworks

```python
from cybernetics_agent.adapters import (
    NativeAdapter,       # Pure Python
    LangChainAdapter,    # LangChain
    AutoGenAdapter,      # AutoGen
    CrewAIAdapter,       # CrewAI
    HermesAdapter,       # Hermes Agent
    ClaudeCodeAdapter,   # Claude Code CLI
    CodexAdapter,        # OpenAI Codex CLI
    OpenClawAdapter,     # OpenClaw (HTTP)
    QwenpawAdapter,      # Qwenpaw
)
```

## 📁 CLI Tools

```bash
cybernetix init              # Initialize config
cybernetix audit ./src       # Audit code defects
cybernetix dashboard         # Launch monitoring dashboard
cybernetix run ./task.py     # Run task and collect metrics
```

## 📝 License

MIT License © 2026 Cybernetics Agent Contributors
