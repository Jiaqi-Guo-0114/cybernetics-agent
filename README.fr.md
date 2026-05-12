# 🦙 Cybernetics Agent

> Une couche d'amélioration cybernétique indépendante du framework pour les agents IA.
> Basée sur les sept principes fondamentaux de l'*Ingénierie Cybernétique* de H.S. Tsien, permettant à tout agent Python d'être auto-adaptatif, auto-réparant et auto-optimisant.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-15%2F15-brightgreen.svg)]()

🌐 **[Français](README.fr.md)** · [中文](README.md) · [English](README.en.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

---

## ✅ Fonctionnalités

- **Indépendant du framework** — Bibliothèque standard pure, zéro dépendance externe
- **Sept Principes** — Couverture complète de l'*Ingénierie Cybernétique* de Tsien
- **Adaptateurs multi-frameworks** — LangChain, AutoGen, CrewAI, Hermes, Claude Code, Codex, etc.
- **Configuration déclarative** — Configuration JSON/YAML, flexible et contrôlable
- **CLI complète** — Outils en ligne de commande `cybernetix` (init / audit / dashboard / run)
- **Thread-safe** — Verrous de threading intégrés pour la sécurité

## 🚀 Démarrage Rapide

```bash
# Installation
pip install cybernetics-agent

# Initialiser la configuration
cybernetix init

# Utilisation
python -c "
from cybernetics_agent import CyberneticsConfig, CyberneticsContext
ctx = CyberneticsContext(CyberneticsConfig(project_name='mon-agent'))
ctx.emit_tool_result('search', ['article1', 'article2'])
print(ctx.get_status())
"
```

## 🎯 Sept Principes

| Principe | Module | Fonction |
|----------|--------|----------|
| 1. Boucle de rétroaction | FeedbackLoop | Actions basées sur déclencheurs, ajustement automatique |
| 2. Stabilité prioritaire | StabilityEngine | Réessai, disjoncteur, dégradation, timeout |
| 3. Identification système | SystemIdentifier | Entonnoir de conversion, métriques d'efficacité |
| 4. Contrôle optimal | OptimalController | Gestion budget, vérification contraintes |
| 5. Théorie de l'information | InfoFlow | Filtrage messages, distribution |
| 6. Contrôle adaptatif | AdaptiveTuner | Auto-ajustement paramètres |
| 7. Contrôle hiérarchique | HierarchyController | Couches Stratégique / Tactique / Exécutive |

## 🔧 Frameworks Supportés

```python
from cybernetics_agent.adapters import (
    NativeAdapter,       # Python pur
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

## 📁 Outils CLI

```bash
cybernetix init              # Initialiser config
cybernetix audit ./src       # Auditer défauts code
cybernetix dashboard         # Lancer tableau de bord
cybernetix run ./task.py     # Exécuter tâche et collecter métriques
```

## 📊 Tableau de Bord

![Dashboard Preview](assets/dashboard_preview.png)

Lancer le tableau de bord:
```bash
cybernetix dashboard
```

## 📝 Licence

MIT License © 2026 Cybernetics Agent Contributors
