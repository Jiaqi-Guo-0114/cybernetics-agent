# Changelog

## [0.6.2] - 2026-05-15

### Fixed
- **Dashboard 中文乱码** — FastAPI `HTMLResponse` 显式设置 `charset=utf-8`，确保 CJK 字符正确渲染
- **版本号一致性** — 修复 `__init__.py`、`dashboard.py`、`dashboard_fastapi.py` 中的版本号与 `pyproject.toml` 不一致的问题

### Changed
- **吉祥物更新** — 将 🦙 羊驼替换为 🐙 章鱼（分布式神经系统 = 分层控制的完美隐喻），覆盖6个 README、2个示例、2个 Dashboard 文件、report、小红书帖子

### Added
- **pytest-cov** — 添加到 `pyproject.toml` dev 依赖，支持本地覆盖率检查

## [0.6.1] - 2026-05-13

### Added
- **核心基类测试** — `core/base.py` (EventType, CyberneticsEvent, ICyberneticsModule) + `alert/channels/base.py` (AlertChannel)
  - 25 个新增测试，基类模块覆盖率 96%–100%
- **复杂分支补齐** — feedback_loop、system_identifier、hierarchy_controller、info_flow 剩余未覆盖行
  - 61 个新增测试，覆盖异常分支、边界条件、隐藏逻辑
  - system_identifier → 100%，hierarchy_controller → 100%，info_flow → 100%，feedback_loop → 99%
- **性能基准测试** — pytest-benchmark 套件
  - 核心模块 7 个：单事件处理 + 批量 100 事件处理
  - Runtime 模块 3 个：EventBus、MetricsCollector、EventStore
  - 23 个 benchmark 测试全部通过
- **CI 覆盖率检查** — GitHub Actions 新增 `--cov-fail-under=90`
- **测试覆盖率大幅提升** — 从 58% → 98%（+40%）
  - 新增 720+ 测试用例，总计 876 个测试全部通过
  - 核心模块全覆盖：AdaptiveTuner（99%）、OptimalController（99%）、StabilityEngine（99%）、FeedbackLoop（99%）、SystemIdentifier（100%）、HierarchyController（100%）、InfoFlow（100%）、base
  - Runtime 层全覆盖：EventBus、EventStore（100%）、MetricsCollector（98%）、PluginLoader、StateManager（99%）
  - Alert 层全覆盖：6 个渠道（含错误处理 mock）、Manager、Rules、AlertChannel
  - Config 与 Context 覆盖率 94%–97%
  - 新增 `.coveragerc` 配置文件，omit adapters/ 和 cli/ 目录
- **Bug 修复**: EventStore.prune() TypeError、context.py Path 导入

## [0.6.0] - 2026-05-13

### Added
- **事件持久化** (EventStore)
  - `runtime/event_store.py`: SQLite 存储层，零外部依赖
  - 三个表：`events`、`metrics`、`alerts`，带索引加速查询
  - 支持按时间范围、类型、严重级别筛选查询
  - 自动清理超过 30 天的旧数据
- **集成点**
  - MetricsCollector 自动将所有事件写入 SQLite
  - AlertManager 自动将触发的告警写入 SQLite
  - Dashboard 新增 `/api/history/*` 端点
- **Bug 修复**: EventStore 目录自动创建、Dashboard 版本号统一、SQLite 异常保护

### Previous Versions
See [Git history](https://github.com/Jiaqi-Guo-0114/cybernetics-agent/commits/main) for earlier releases (v0.1.0–v0.5.0).
