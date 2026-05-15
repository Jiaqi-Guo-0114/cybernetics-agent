# Dashboard

> 实时监控你的 Agent——事件流、指标趋势、告警面板，一目了然。

---

## 启动

```bash
# 默认配置
cybernetix dashboard

# 指定配置
cybernetix dashboard --config cfg.json --host 0.0.0.0 --port 8080

# 查看帮助
cybernetix dashboard --help
```

启动后访问：
- **Dashboard**: http://localhost:8080
- **Prometheus**: http://localhost:8080/metrics
- **API**: http://localhost:8080/api/metrics

---

## 功能概览

### 实时指标面板

Dashboard 首页显示核心指标的实时数值：

| 指标 | 说明 |
|------|------|
| 工具调用 | 累计 tool 调用次数 |
| 工具成功率 | 成功调用 / 总调用 |
| LLM 调用 | 累计 LLM 调用次数 |
| LLM 成功率 | 成功调用 / 总调用 |
| 错误总数 | 累计错误次数 |
| 会话 ID | 当前会话标识 |

数据每 3 秒自动刷新。

### 七大原则模块状态

可视化展示每个控制论模块的启用状态：

- ✅ 反馈闭环
- ✅ 稳定性引擎
- ✅ 系统辨识
- ✅ 最优控制
- ✅ 信息流
- ✅ 自适应调谐
- ✅ 分层控制

### 告警面板

显示当前告警规则、渠道健康状态和最近告警历史：

```
规则 (3): high_error_rate, api_timeout, budget_exceeded
渠道: stdout(✓), feishu(✓), discord(✗)

最近告警:
[14:32:15] high_error_rate | 错误率超过 10%
[14:28:02] api_timeout | LLM 调用超时
```

数据每 5 秒自动刷新。

---

## API 端点

### 实时数据

| 端点 | 说明 | 格式 |
|------|------|------|
| `GET /` | Dashboard 页面 | HTML |
| `GET /metrics` | Prometheus 指标 | OpenMetrics |
| `GET /api/status` | 系统状态 | JSON |
| `GET /api/config` | 当前配置 | JSON |
| `GET /api/metrics` | 指标摘要 | JSON |
| `GET /api/events` | SSE 事件流 | text/event-stream |

### 历史查询（v0.6.0+）

| 端点 | 参数 | 说明 |
|------|------|------|
| `GET /api/history/events` | `from`, `to`, `type`, `limit` | 历史事件查询 |
| `GET /api/history/metrics` | `metric`, `from`, `to`, `limit` | 历史指标查询 |
| `GET /api/history/alerts` | `from`, `to`, `severity`, `limit` | 历史告警查询 |
| `GET /api/history/stats` | 无 | 统计摘要 |

### 告警管理

| 端点 | 说明 |
|------|------|
| `GET /alert/status` | 告警系统状态 |

---

## Prometheus 集成

`/metrics` 端点输出标准 OpenMetrics 格式，可直接被 Prometheus 抓取：

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'cybernetics-agent'
    static_configs:
      - targets: ['localhost:8080']
```

---

## 配置热重载

Dashboard 启动后自动监听配置文件变更：

```bash
cybernetix dashboard --config cfg.json
# 修改 cfg.json
# → 5秒后配置自动重载
# → AlertManager 重新初始化
# → 新规则立即生效
```

---

## 事件持久化

v0.6.0+ 所有事件、指标、告警历史自动写入 SQLite，进程重启不丢失：

```python
from cybernetics_agent.runtime.event_store import EventStore

store = EventStore()

# 查询历史事件
events = store.query_events(
    from_time=time.time() - 3600,  # 过去1小时
    event_type="tool_error",
    limit=100,
)

# 查询历史指标
metrics = store.query_metrics(
    metric_name="error_rate",
    from_time=time.time() - 86400,  # 过去24小时
)

# 查询历史告警
alerts = store.query_alerts(
    severity="critical",
    limit=50,
)
```

---

## 前端自定义

Dashboard 前端是内嵌的 HTML/JS，你可以：

1. **修改主题色**: 编辑 `cli/dashboard.py` 或 `cli/dashboard_fastapi.py` 中的 CSS
2. **添加自定义面板**: 在 HTML 模板中新增 `<div>` 和对应的 JS 刷新逻辑
3. **接入 Grafana**: 使用 `/metrics` 端点 + Prometheus 数据源

---

## 部署建议

### 本地开发

```bash
cybernetix dashboard --port 8080
```

### 生产环境

使用 gunicorn + uvicorn 部署 FastAPI 版本：

```bash
pip install gunicorn uvicorn
gunicorn -w 2 -k uvicorn.workers.UvicornWorker cybernetics_agent.cli.dashboard_fastapi:app
```

或使用 Docker：

```dockerfile
FROM python:3.11-slim
RUN pip install cybernetics-agent[dashboard]
COPY cfg.json /app/cfg.json
CMD ["cybernetix", "dashboard", "--config", "/app/cfg.json", "--host", "0.0.0.0"]
```
