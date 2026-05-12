"""
dashboard 命令。

启动本地 Web 仪表盘展示系统状态。
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict


def run_dashboard(args: Namespace) -> int:
    """执行 dashboard 命令。"""
    host = args.host
    port = args.port

    print(f"📊 启动 Cybernetics Dashboard...")
    print(f"   地址: http://{host}:{port}")
    print(f"   配置: {args.config}")
    print()

    # 检查配置文件
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"⚠️  配置文件不存在: {config_path}")
        print("请先运行: cybernetix init")
        return 1

    # 启动 HTTP 服务器
    try:
        start_http_server(host, port, config_path)
    except KeyboardInterrupt:
        print("\n👋 Dashboard 已关闭")
        return 0

    return 0


def start_http_server(host: str, port: int, config_path: Path) -> None:
    """启动简单的 HTTP 服务器。"""
    from http.server import BaseHTTPRequestHandler, HTTPServer

    # 加载配置
    config = json.loads(config_path.read_text(encoding="utf-8"))

    class DashboardHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            # 隐藏日志输出
            pass

        def do_GET(self) -> None:
            if self.path == "/" or self.path == "/index.html":
                self._serve_html()
            elif self.path == "/api/status":
                self._serve_api_status()
            elif self.path == "/api/config":
                self._serve_api_config()
            else:
                self.send_error(404)

        def _serve_html(self) -> None:
            html = _generate_dashboard_html(config)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        def _serve_api_status(self) -> None:
            status = {
                "status": "running",
                "timestamp": __import__("time").time(),
                "config_loaded": config_path.name,
            }
            self._send_json(status)

        def _serve_api_config(self) -> None:
            self._send_json(config)

        def _send_json(self, data: Dict[str, Any]) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    server = HTTPServer((host, port), DashboardHandler)
    print(f"✅ Dashboard 已在 http://{host}:{port} 运行")
    print("按 Ctrl+C 停止")
    server.serve_forever()


def _generate_dashboard_html(config: Dict[str, Any]) -> str:
    """生成 Dashboard HTML 页面。"""
    project_name = config.get("project_name", "Cybernetics Agent")

    modules = []
    module_configs = [
        ("反馈闭环", "feedback_loop", config.get("feedback_loop", {})),
        ("稳定性引擎", "stability", config.get("stability", {})),
        ("系统辨识", "system_id", config.get("system_id", {})),
        ("最优控制", "optimal_control", config.get("optimal_control", {})),
        ("信息流", "info_flow", config.get("info_flow", {})),
        ("自适应调谐", "adaptive", config.get("adaptive", {})),
        ("分层控制", "hierarchy", config.get("hierarchy", {})),
    ]

    for name, key, cfg in module_configs:
        enabled = cfg.get("enabled", False)
        status = "✅ 已启用" if enabled else "⚠️ 未启用"
        modules.append(f"""
        <div class="module-card">
            <h3>{name}</h3>
            <span class="status-badge {'enabled' if enabled else 'disabled'}">{status}</span>
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
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
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
    </header>
    <div class="container">
        <h2>七大原则模块状态</h2>
        <div class="modules-grid">
            {''.join(modules)}
        </div>
    </div>
    <div class="footer">
        <p>Cybernetics Agent v1.0 | 基于钱学森工程控制论</p>
    </div>
    <script>
        // 定期刷新状态
        setInterval(async () => {{
            try {{
                const res = await fetch('/api/status');
                const data = await res.json();
                console.log('Status:', data.status);
            }} catch (e) {{
                console.error('Failed to fetch status');
            }}
        }}, 5000);
    </script>
</body>
</html>"""
