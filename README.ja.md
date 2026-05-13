# 🦙 Cybernetics Agent

> フレームワーク非依存のサイバネティクス強化層。
> 錦学森《工程制御論》の7大核心原則に基づき、いかなる Python Agent も自适応、自修復、自最適化の能力を获得。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-93%2F93-brightgreen.svg)]()

🌐 **[日本語](README.ja.md)** · [中文](README.md) · [English](README.en.md) · [Français](README.fr.md) · [Español](README.es.md) · [한국어](README.ko.md)

---

## ✅ 特徴

- **フレームワーク非依存** — 純正スタンダードライブラリ、外部依存なし
- **7大原則** — 錦学森《工程制御論》完全カバー
- **多フレームワークアダプタ** — LangChain、AutoGen、CrewAI、Hermes、Claude Code、Codex など
- **宣言的設定** — JSON/YAML 構成、柔軟かつ可制御
- **完備な CLI** — `cybernetix` コマンドラインツール（init / audit / dashboard / run）
- **スレッドセーフ** — 内蔵のスレッドロック保護

## 🚀 クイックスタート

```bash
# インストール
pip install cybernetics-agent

# 設定の初期化
cybernetix init

# 使用
python -c "
from cybernetics_agent import CyberneticsConfig, CyberneticsContext
ctx = CyberneticsContext(CyberneticsConfig(project_name='my-agent'))
ctx.emit_tool_result('search', ['paper1', 'paper2'])
print(ctx.get_status())
"
```

## 🎯 7大原則

| 原則 | モジュール | 機能 |
|------|--------|------|
| 1. フィードバックループ | FeedbackLoop | トリガーアクション、自動調整 |
| 2. 安定性優先 | StabilityEngine | リトライ、サーキットブレーカー、デグレード、タイムアウト |
| 3. システム同定 | SystemIdentifier | 転化ファネル、効率指標収集 |
| 4. 最適制御 | OptimalController | 予算管理、制約チェック |
| 5. 情報理論 | InfoFlow | メッセージフィルタリング、配信 |
| 6. 自适応制御 | AdaptiveTuner | パラメータ自動調整 |
| 7. 階層制御 | HierarchyController | 戦略/戦術/実行の3層構造 |

## 🔧 サポートフレームワーク

```python
from cybernetics_agent.adapters import (
    NativeAdapter,       # 純正 Python
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

## 📁 CLI ツール

```bash
cybernetix init              # 設定の初期化
cybernetix audit ./src       # コード欠陰のアディット
cybernetix dashboard         # 監視ダッシュボード起動
cybernetix run ./task.py     # タスク実行と指標収集
```

## 📊 ダッシュボード

![Dashboard Preview](assets/dashboard_preview.png)

ダッシュボード起動:
```bash
cybernetix dashboard
```

## 📝 ライセンス

MIT License © 2026 Cybernetics Agent Contributors
