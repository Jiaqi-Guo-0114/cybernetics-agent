# 🦙 Cybernetics Agent

> A framework-agnostic cybernetics enhancement layer for AI agents.
> Based on H.S. Tsien's *Engineering Cybernetics* seven core principles, enabling any Python agent with self-adaptive, self-healing, and self-optimizing capabilities.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-93%2F93-brightgreen.svg)]()

🌐 **[English](README.en.md)** · [中文](README.md) · [Français](README.fr.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

---

## ✅ Features

- **Framework-agnostic** — No dependency on any LLM framework, pure stdlib
- **Seven Principles** — Full coverage of Qian Xuesen's Engineering Cybernetics
- **Multi-framework Adapters** — LangChain, AutoGen, CrewAI, Hermes, Claude Code, Codex, etc.
- **Declarative Config** — JSON/YAML configuration, flexible and controllable
- **Strategy Presets** — 4 out-of-the-box templates (high-concurrency / low-cost / high-reliability / debug)
- **Metrics Export** — Prometheus / OpenMetrics text format, Grafana-ready
- **Plugin System** — Hot-swappable custom modules, auto-discovery
- **Real-time Dashboard** — FastAPI + SSE streaming, live frontend
- **Auto-tuning** — ε-greedy parameter optimization with confidence scoring
- **Full CLI Toolkit** — `cybernetix` (init / audit / dashboard / preset / plugin / validate / run / --version)
- **Thread-safe** — Built-in thread lock protection

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
cybernetix init                          # Initialize config
cybernetix preset list                   # List strategy presets
cybernetix preset show <name>            # Show preset details
cybernetix preset apply <name> -o cfg.json  # Apply preset
cybernetix validate cfg.json             # Validate config file
cybernetix plugin list                   # List plugins
cybernetix plugin discover               # Discover plugins
cybernetix dashboard                     # Launch monitoring dashboard
cybernetix audit ./src                   # Audit code issues
cybernetix run ./task.py                 # Run task with metrics
cybernetix --version                     # Show version
```

## 📊 Dashboard

![Dashboard Preview](assets/dashboard_preview.png)

Launch dashboard:
```bash
cybernetix dashboard
```

## 📝 License

MIT License © 2026 Cybernetics Agent Contributors
