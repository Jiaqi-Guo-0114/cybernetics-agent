"""

FastAPI Dashboard 实现。

提供真正的 Web 仪表盘服务，支持 SSE 实时事件流。
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from ..config import CyberneticsConfig
from ..context import CyberneticsContext

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, StreamingResponse
    from fastapi.staticfiles import StaticFiles
    from starlette.middleware.cors import CORSMiddleware
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


def create_app(config: CyberneticsConfig, ctx: CyberneticsContext, alert_manager: Any | None = None, event_store: Any | None = None) -> Any | None:
    """创建 FastAPI 应用。"""
    if not HAS_FASTAPI:
        return None

    app = FastAPI(title="Cybernetics Dashboard", version="0.6.3")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载独立前端静态文件
    import cybernetics_agent
    static_dir = Path(cybernetics_agent.__file__).parent.parent.parent / "dashboard_static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    async def index() -> HTMLResponse:
        # 优先使用独立前端
        if static_dir.exists():
            html_path = static_dir / "index.html"
            if html_path.exists():
                return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
        # 回退到内嵌 HTML
        return HTMLResponse(
            content=_generate_dashboard_html(config, ctx),
            media_type="text/html; charset=utf-8",
        )

    @app.get("/metrics")
    async def prometheus_metrics() -> str:
        return ctx.metrics.to_prometheus()

    @app.get("/api/status")
    async def api_status() -> dict[str, Any]:
        status = ctx.get_status()
        status["timestamp"] = time.time()
        return status

    @app.get("/api/config")
    async def api_config() -> dict[str, Any]:
        return config.to_dict()

    @app.get("/api/metrics")
    async def api_metrics() -> dict[str, Any]:
        summary = ctx.metrics.get_summary()
        summary["timestamp"] = time.time()
        return summary

    @app.get("/health")
    async def health() -> dict[str, Any]:
        """基本健康检查。返回 HTTP 200 表示服务活着。"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "0.6.3",
        }

    @app.get("/ready")
    async def ready() -> dict[str, Any]:
        """就绪检查。检查各模块是否正常运行。"""
        try:
            status = ctx.get_status()
            modules = status.get("modules", {})
            total_modules = len(modules)
            healthy_modules = sum(
                1 for m in modules.values()
                if isinstance(m, dict) and m.get("enabled", False)
            )

            is_ready = total_modules > 0 and healthy_modules == total_modules

            return {
                "status": "ready" if is_ready else "not_ready",
                "timestamp": time.time(),
                "modules": {
                    "total": total_modules,
                    "healthy": healthy_modules,
                },
            }
        except Exception as e:
            return {
                "status": "not_ready",
                "timestamp": time.time(),
                "error": str(e),
            }

    @app.get("/api/events")
    async def event_stream(request: Request) -> StreamingResponse:
        async def generator() -> AsyncGenerator[str, None]:
            last_index = 0
            while True:
                if await request.is_disconnected():
                    break
                events = ctx.metrics._raw_events
                if len(events) > last_index:
                    for evt in events[last_index:]:
                        yield f"data: {json.dumps(evt, default=str)}\n\n"
                    last_index = len(events)
                await asyncio.sleep(1)

        return StreamingResponse(
            generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    if alert_manager is not None:
        @app.get("/alert/status")
        async def alert_status() -> dict[str, Any]:
            return alert_manager.get_status()

    if event_store is not None:
        @app.get("/api/history/events")
        async def history_events(
            from_time: float | None = None,
            to_time: float | None = None,
            event_type: str | None = None,
            limit: int = 100,
        ) -> list[dict[str, Any]]:
            return event_store.query_events(from_time=from_time, to_time=to_time, event_type=event_type, limit=limit)

        @app.get("/api/history/metrics")
        async def history_metrics(
            metric_name: str | None = None,
            from_time: float | None = None,
            to_time: float | None = None,
            limit: int = 100,
        ) -> list[dict[str, Any]]:
            return event_store.query_metrics(metric_name=metric_name, from_time=from_time, to_time=to_time, limit=limit)

        @app.get("/api/history/alerts")
        async def history_alerts(
            from_time: float | None = None,
            to_time: float | None = None,
            severity: str | None = None,
            limit: int = 100,
        ) -> list[dict[str, Any]]:
            return event_store.query_alerts(from_time=from_time, to_time=to_time, severity=severity, limit=limit)

        @app.get("/api/history/stats")
        async def history_stats() -> dict[str, Any]:
            return event_store.get_stats()

    return app


def run_fastapi_server(
    host: str,
    port: int,
    config: CyberneticsConfig,
    ctx: CyberneticsContext,
    alert_manager: Any | None = None,
    event_store: Any | None = None,
) -> bool:
    """启动 FastAPI 服务器。返回 True 表示成功。"""
    if not HAS_FASTAPI:
        return False

    import uvicorn
    app = create_app(config, ctx, alert_manager=alert_manager, event_store=event_store)
    if app is None:
        return False

    uvicorn.run(app, host=host, port=port, log_level="warning")
    return True


def _generate_dashboard_html(config: CyberneticsConfig, ctx: CyberneticsContext) -> str:
    """生成 Dashboard HTML 页面（SSE 版本）。"""
    project_name = config.project_name
    status = ctx.get_status()
    modules = []
    module_configs = [
        ("反馈闭环", "feedback_loop", status.get("modules", {}).get("feedback_loop", {})),
        ("稳定性引擎", "stability", status.get("modules", {}).get("stability", {})),
        ("系统辨识", "system_id", status.get("modules", {}).get("system_id", {})),
        ("最优控制", "optimal_control", status.get("modules", {}).get("optimal_control", {})),
        ("信息流", "info_flow", status.get("modules", {}).get("info_flow", {})),
        ("自适应调谐", "adaptive", status.get("modules", {}).get("adaptive", {})),
        ("分层控制", "hierarchy", status.get("modules", {}).get("hierarchy", {})),
    ]

    for name, key, cfg in module_configs:
        enabled = cfg.get("enabled", False) if isinstance(cfg, dict) else False
        status_text = "✅ 已启用" if enabled else "⚠️ 未启用"
        modules.append(f"""
        <div class="module-card">
            <h3>{name}</h3>
            <span class="status-badge {'enabled' if enabled else 'disabled'}">{status_text}</span>
            <p>模块 ID: <code>{key}</code></p>
        </div>
        """)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Cybernetics Dashboard</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f23;
            color: #e0e0e0;
            min-height: 100vh;
        }}
        header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 40px 20px;
            text-align: center;
            border-bottom: 1px solid #2a2a4a;
        }}
        header h1 {{ font-size: 2.5em; margin-bottom: 10px; color: #fff; }}
        header p {{ color: #888; font-size: 1.1em; }}
        .links {{
            margin-top: 15px;
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .links a {{
            color: #6c7ae0;
            text-decoration: none;
            padding: 6px 14px;
            border: 1px solid #2a2a4a;
            border-radius: 6px;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        .links a:hover {{
            border-color: #6c7ae0;
            background: rgba(108, 122, 224, 0.1);
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .metrics-panel {{
            background: #1a1a2e;
            border: 1px solid #2a2a4a;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
        }}
        .metrics-panel h2 {{
            font-size: 1.3em;
            margin-bottom: 16px;
            color: #fff;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
        }}
        .metric-item {{
            background: #0f0f23;
            border-radius: 8px;
            padding: 16px;
        }}
        .metric-item .label {{
            color: #888;
            font-size: 0.85em;
            margin-bottom: 6px;
        }}
        .metric-item .value {{
            font-size: 1.6em;
            font-weight: 600;
            color: #6c7ae0;
        }}
        .event-log {{
            background: #0f0f23;
            border-radius: 8px;
            padding: 16px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.85em;
        }}
        .event-log .event-line {{
            padding: 4px 0;
            border-bottom: 1px solid #1a1a2e;
            color: #aaa;
        }}
        .event-log .event-line:last-child {{
            border-bottom: none;
        }}
        .modules-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .module-card {{
            background: #1a1a2e;
            border: 1px solid #2a2a4a;
            border-radius: 12px;
            padding: 24px;
            transition: transform 0.2s, border-color 0.2s;
        }}
        .module-card:hover {{
            transform: translateY(-4px);
            border-color: #4a4a8a;
        }}
        .module-card h3 {{
            font-size: 1.3em;
            margin-bottom: 12px;
            color: #fff;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .status-badge.enabled {{
            background: rgba(40, 167, 69, 0.2);
            color: #28a745;
        }}
        .status-badge.disabled {{
            background: rgba(255, 193, 7, 0.2);
            color: #ffc107;
        }}
        .module-card p {{
            margin-top: 12px;
            color: #888;
            font-size: 0.9em;
        }}
        .module-card code {{
            background: #2a2a4a;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .footer {{
            text-align: center;
            padding: 40px;
            color: #666;
            border-top: 1px solid #2a2a4a;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>🐙 Cybernetics Agent</h1>
        <p>{project_name} - 系统状态仪表盘</p>
        <div class="links">
            <a href="/metrics" target="_blank">📊 Prometheus /metrics</a>
            <a href="/api/metrics" target="_blank">📊 JSON API</a>
            <a href="/api/status" target="_blank">🔍 Status API</a>
        </div>
    </header>
    <div class="container">
        <div class="metrics-panel">
            <h2>📊 实时指标</h2>
            <div class="metric-grid" id="metrics-grid">
                <div class="metric-item">
                    <div class="label">工具调用</div>
                    <div class="value" id="tool-calls">-</div>
                </div>
                <div class="metric-item">
                    <div class="label">工具成功率</div>
                    <div class="value" id="tool-success">-</div>
                </div>
                <div class="metric-item">
                    <div class="label">LLM 调用</div>
                    <div class="value" id="llm-calls">-</div>
                </div>
                <div class="metric-item">
                    <div class="label">LLM 成功率</div>
                    <div class="value" id="llm-success">-</div>
                </div>
                <div class="metric-item">
                    <div class="label">错误总数</div>
                    <div class="value" id="errors">-</div>
                </div>
                <div class="metric-item">
                    <div class="label">会话 ID</div>
                    <div class="value" id="session-id" style="font-size:0.9em">-</div>
                </div>
            </div>
        </div>
        <div class="metrics-panel">
            <h2>📡 实时事件流</h2>
            <div class="event-log" id="event-log">
                <div class="event-line">等待事件...</div>
            </div>
        </div>
        <div class="metrics-panel">
            <h2>告警状态</h2>
            <div id="alert-panel">
                <p style="color:#888">加载中...</p>
            </div>
        </div>
        <h2>七大原则模块状态</h2>
        <div class="modules-grid">
            {''.join(modules)}
        </div>
    </div>
    <div class="footer">
        <p>🐙 Cybernetics Agent v0.6.3 | 基于钱学森工程控制论</p>
    </div>
    <script>
        async function refreshMetrics() {{
            try {{
                const res = await fetch('/api/metrics');
                const data = await res.json();

                const tc = data.counters?.tool_calls_total || {{}};
                const toolCalls = Object.values(tc).reduce((a, b) => a + b, 0);
                document.getElementById('tool-calls').textContent = toolCalls;

                const te = data.counters?.tool_errors_total || {{}};
                const toolErrors = Object.values(te).reduce((a, b) => a + b, 0);
                const tsr = toolCalls > 0 ? ((toolCalls - toolErrors) / toolCalls * 100).toFixed(1) + '%' : 'N/A';
                document.getElementById('tool-success').textContent = tsr;

                const lc = data.counters?.llm_calls_total || {{}};
                const llmCalls = Object.values(lc).reduce((a, b) => a + b, 0);
                document.getElementById('llm-calls').textContent = llmCalls;

                const le = data.counters?.llm_errors_total || {{}};
                const llmErrors = Object.values(le).reduce((a, b) => a + b, 0);
                const lsr = llmCalls > 0 ? ((llmCalls - llmErrors) / llmCalls * 100).toFixed(1) + '%' : 'N/A';
                document.getElementById('llm-success').textContent = lsr;

                const err = data.counters?.errors_total || {{}};
                const errTotal = Object.values(err).reduce((a, b) => a + b, 0);
                document.getElementById('errors').textContent = errTotal;
            }} catch (e) {{
                console.error('Failed to fetch metrics:', e);
            }}
        }}

        async function refreshStatus() {{
            try {{
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('session-id').textContent = data.session_id || '-';
            }} catch (e) {{}}
        }}

        async function refreshAlerts() {{
            try {{
                const res = await fetch('/alert/status');
                if (!res.ok) {{
                    document.getElementById('alert-panel').innerHTML = '<p style="color:#888">未启用告警系统</p>';
                    return;
                }}
                const data = await res.json();
                let html = '<div style="margin-bottom:12px;">';
                html += '<strong>规则 (' + data.rules.length + '):</strong> ';
                html += data.rules.map(r => r.name).join(', ') || '无';
                html += '</div>';
                html += '<div style="margin-bottom:12px;">';
                html += '<strong>渠道:</strong> ';
                html += data.channels.map(c => c.name + (c.healthy ? '(✓)' : '(✗)')).join(', ') || '无';
                html += '</div>';
                if (data.history.length > 0) {{
                    html += '<div><strong>最近告警:</strong></div>';
                    html += '<div class="event-log" style="margin-top:8px;">';
                    data.history.slice(-10).reverse().forEach(h => {{
                        const t = new Date(h.timestamp * 1000).toLocaleTimeString();
                        const sev = h.severity || 'warning';
                        const color = sev === 'critical' ? '#ff4444' : sev === 'error' ? '#ff8800' : '#aaa';
                        html += '<div class="event-line" style="color:' + color + '">[' + t + '] ' + h.rule_name + ' | ' + h.message + '</div>';
                    }});
                    html += '</div>';
                }}
                document.getElementById('alert-panel').innerHTML = html;
            }} catch (e) {{
                document.getElementById('alert-panel').innerHTML = '<p style="color:#888">未启用告警系统</p>';
            }}
        }}

        function connectSSE() {{
            const log = document.getElementById('event-log');
            const evtSource = new EventSource('/api/events');
            let count = 0;

            evtSource.onmessage = (e) => {{
                try {{
                    const data = JSON.parse(e.data);
                    const line = document.createElement('div');
                    line.className = 'event-line';
                    const time = new Date(data.timestamp * 1000).toLocaleTimeString();
                    line.textContent = `[${{time}}] ${{data.event_type}} | ${{JSON.stringify(data.payload).slice(0, 80)}}`;
                    log.insertBefore(line, log.firstChild);
                    count++;
                    if (count > 50) log.lastChild.remove();
                }} catch (err) {{
                    console.error('SSE parse error:', err);
                }}
            }};

            evtSource.onerror = () => {{
                console.log('SSE disconnected, retrying...');
            }};
        }}

        refreshMetrics();
        refreshStatus();
        refreshAlerts();
        connectSSE();
        setInterval(refreshMetrics, 3000);
        setInterval(refreshStatus, 10000);
        setInterval(refreshAlerts, 5000);
    </script>
</body>
</html>"""
