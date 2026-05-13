"""
dashboard 命令。

启动本地 Web 仪表盘，支持 Prometheus /metrics 端点。

优先使用 FastAPI（如果安装了 [dashboard] 可选依赖），
否则回退到标准库 http.server。
"""

from __future__ import annotations

import json
import time
from argparse import Namespace
from pathlib import Path
from typing import Any

from ..config import CyberneticsConfig
from ..context import CyberneticsContext


def run_dashboard(args: Namespace) -> int:
    """执行 dashboard 命令。"""
    host = args.host
    port = args.port
    config_path = Path(args.config)

    if config_path.exists():
        config = CyberneticsConfig.from_json(config_path)
    else:
        print(f"  配置文件不存在: {config_path}")
        print("先运行: cybernetix init")
        return 1

    ctx = CyberneticsContext(config)

    # 创建 AlertManager
    alert_manager = None
    alert_cfg = config.to_dict().get("alert", {})
    if alert_cfg.get("enabled", False):
        from ..alert import AlertManager, ThresholdRule
        from ..alert.channels import StdoutChannel
        alert_manager = AlertManager()
        alert_manager.register_channel("stdout", StdoutChannel())
        for rule_cfg in alert_cfg.get("rules", []):
            if rule_cfg.get("type") == "threshold":
                alert_manager.add_rule(ThresholdRule(
                    name=rule_cfg["name"],
                    metric=rule_cfg["metric"],
                    operator=rule_cfg["operator"],
                    threshold=rule_cfg["threshold"],
                    duration=rule_cfg.get("duration", 0),
                    severity=rule_cfg.get("severity", "warning"),
                ))

    # 创建 ConfigWatcher
    watcher = None
    if config_path.exists():
        from ..runtime.config_watcher import ConfigWatcher
        def reload_config():
            nonlocal config, ctx, alert_manager
            print(f"\n  配置文件变更，重新加载...")
            try:
                config = CyberneticsConfig.from_json(config_path)
                ctx.shutdown()
                ctx = CyberneticsContext(config)
                # 重新加载 AlertManager
                alert_cfg = config.to_dict().get("alert", {})
                if alert_cfg.get("enabled", False):
                    from ..alert import AlertManager, ThresholdRule
                    from ..alert.channels import StdoutChannel
                    alert_manager = AlertManager()
                    alert_manager.register_channel("stdout", StdoutChannel())
                    for rule_cfg in alert_cfg.get("rules", []):
                        if rule_cfg.get("type") == "threshold":
                            alert_manager.add_rule(ThresholdRule(
                                name=rule_cfg["name"],
                                metric=rule_cfg["metric"],
                                operator=rule_cfg["operator"],
                                threshold=rule_cfg["threshold"],
                                duration=rule_cfg.get("duration", 0),
                                severity=rule_cfg.get("severity", "warning"),
                            ))
                print("✅ 配置已重新加载\n")
            except Exception as e:
                print(f"  重新加载失败: {e}")
        watcher = ConfigWatcher(str(config_path), reload_config, interval=5.0)
        watcher.start()

    print("启动 Cybernetics Dashboard...")
    print(f"   地址: http://{host}:{port}")
    print(f"   Prometheus: http://{host}:{port}/metrics")
    print(f"   API: http://{host}:{port}/api/metrics")
    if watcher:
        print(f"   热重载: 已启用 (监听 {config_path})")
    print()

    # 尝试 FastAPI
    try:
        from .dashboard_fastapi import run_fastapi_server
        if run_fastapi_server(host, port, config, ctx, alert_manager=alert_manager):
            return 0
    except Exception as e:
        print(f"FastAPI 启动失败: {e}")
        print("回退到标准库 HTTP 服务器...")
        print()

    # Fallback 到 http.server
    try:
        start_http_server(host, port, config, ctx, alert_manager=alert_manager)
    except KeyboardInterrupt:
        print("\n Dashboard 已关闭")
        if watcher:
            watcher.stop()
        ctx.shutdown()
        return 0

    return 0


def start_http_server(host: str, port: int, config: CyberneticsConfig, ctx: CyberneticsContext, alert_manager: Any | None = None) -> None:
    """启动 HTTP 服务器。"""
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class DashboardHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            pass

        def do_GET(self) -> None:
            if self.path == "/" or self.path == "/index.html":
                self._serve_html()
            elif self.path == "/metrics":
                self._serve_prometheus()
            elif self.path == "/api/status":
                self._serve_api_status()
            elif self.path == "/api/config":
                self._serve_api_config()
            elif self.path == "/api/metrics":
                self._serve_api_metrics()
            elif self.path == "/alert/status" and alert_manager is not None:
                self._serve_alert_status()
            else:
                self.send_error(404)

        def _serve_html(self) -> None:
            html = _generate_dashboard_html(config, ctx, alert_manager=alert_manager)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        def _serve_prometheus(self) -> None:
            body = ctx.metrics.to_prometheus()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def _serve_api_status(self) -> None:
            status = ctx.get_status()
            status["timestamp"] = time.time()
            self._send_json(status)

        def _serve_api_config(self) -> None:
            self._send_json(config.to_dict())

        def _serve_api_metrics(self) -> None:
            summary = ctx.metrics.get_summary()
            summary["timestamp"] = time.time()
            self._send_json(summary)

        def _serve_alert_status(self) -> None:
            self._send_json(alert_manager.get_status())

        def _send_json(self, data: dict[str, Any]) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode("utf-8"))

    server = HTTPServer((host, port), DashboardHandler)
    print(f" Dashboard 已在 http://{host}:{port} 运行")
    print("按 Ctrl+C 停止")
    server.serve_forever()


def _generate_dashboard_html(config: CyberneticsConfig, ctx: CyberneticsContext, alert_manager: Any | None = None) -> str:
    """生成 Dashboard HTML 页面。"""
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
        <h1>🦙 Cybernetics Agent</h1>
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
        <p>Cybernetics Agent v2.0 | 基于钱学森工程控制论</p>
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

        refreshMetrics();
        refreshStatus();
        refreshAlerts();
        setInterval(refreshMetrics, 3000);
        setInterval(refreshStatus, 10000);
        setInterval(refreshAlerts, 5000);
    </script>
</body>
</html>"""
