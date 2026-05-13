# 🦙 Cybernetics Agent

> Una capa de mejora cibernética independiente del framework para agentes de IA.
> Basada en los siete principios fundamentales de la *Cibernética de Ingeniería* de H.S. Tsien, permitiendo que cualquier agente Python sea auto-adaptativo, auto-reparable y auto-optimizante.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-83%2F83-brightgreen.svg)]()

🌐 **[Español](README.es.md)** · [中文](README.md) · [English](README.en.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

---

## ✅ Características

- **Independiente del framework** — Biblioteca estándar pura, cero dependencias externas
- **Siete Principios** — Cobertura completa de la *Cibernética de Ingeniería* de Tsien
- **Adaptadores multi-framework** — LangChain, AutoGen, CrewAI, Hermes, Claude Code, Codex, etc.
- **Configuración declarativa** — Configuración JSON/YAML, flexible y controlable
- **CLI completa** — Herramientas de línea de comandos `cybernetix` (init / audit / dashboard / run)
- **Thread-safe** — Bloqueos de threading integrados para seguridad

## 🚀 Inicio Rápido

```bash
# Instalar
pip install cybernetics-agent

# Inicializar configuración
cybernetix init

# Uso
python -c "
from cybernetics_agent import CyberneticsConfig, CyberneticsContext
ctx = CyberneticsContext(CyberneticsConfig(project_name='mi-agente'))
ctx.emit_tool_result('search', ['paper1', 'paper2'])
print(ctx.get_status())
"
```

## 🎯 Siete Principios

| Principio | Módulo | Función |
|-----------|---------|----------|
| 1. Bucle de retroalimentación | FeedbackLoop | Acciones por disparadores, ajuste automático |
| 2. Estabilidad primero | StabilityEngine | Reintento, disyuntor, degradación, timeout |
| 3. Identificación del sistema | SystemIdentifier | Embudo de conversión, métricas de eficiencia |
| 4. Control óptimo | OptimalController | Gestión de presupuesto, verificación de restricciones |
| 5. Teoría de la información | InfoFlow | Filtrado de mensajes, distribución |
| 6. Control adaptativo | AdaptiveTuner | Auto-ajuste de parámetros |
| 7. Control jerárquico | HierarchyController | Capas Estratégica / Táctica / Ejecutiva |

## 🔧 Frameworks Soportados

```python
from cybernetics_agent.adapters import (
    NativeAdapter,       # Python puro
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

## 📁 Herramientas CLI

```bash
cybernetix init              # Inicializar config
cybernetix audit ./src       # Auditar defectos de código
cybernetix dashboard         # Iniciar panel de control
cybernetix run ./task.py     # Ejecutar tarea y recolectar métricas
```

## 📊 Panel de Control

![Dashboard Preview](assets/dashboard_preview.png)

Iniciar panel de control:
```bash
cybernetix dashboard
```

## 📝 Licencia

MIT License © 2026 Cybernetics Agent Contributors
