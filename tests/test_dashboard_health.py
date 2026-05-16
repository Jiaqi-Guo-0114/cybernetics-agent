"""
Dashboard 健康检查端点测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig
from cybernetics_agent import __version__ as _version
from cybernetics_agent.cli.dashboard_fastapi import create_app
from cybernetics_agent.context import CyberneticsContext

try:
    from fastapi.testclient import TestClient
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


def test_health_endpoint():
    """/health 端点返回健康状态。"""
    if not HAS_FASTAPI:
        return

    cfg = CyberneticsConfig()
    ctx = CyberneticsContext(cfg)
    app = create_app(cfg, ctx)
    if app is None:
        return

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == _version


def test_ready_endpoint_no_modules():
    """没有模块时应该返回 not_ready。"""
    if not HAS_FASTAPI:
        return

    cfg = CyberneticsConfig()
    ctx = CyberneticsContext(cfg)
    app = create_app(cfg, ctx)
    if app is None:
        return

    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["modules"]["total"] == 0


def test_ready_endpoint_with_modules():
    """有模块时应该返回 ready。"""
    if not HAS_FASTAPI:
        return

    from cybernetics_agent.core.base import ICyberneticsModule

    class DummyModule(ICyberneticsModule):
        name = "dummy"
        enabled = True

        def __init__(self):
            super().__init__({}, None)

        def on_event(self, event):
            return event
        def initialize(self): pass
        def shutdown(self): pass
        def get_status(self):
            return {"enabled": True}

    cfg = CyberneticsConfig()
    ctx = CyberneticsContext(cfg)
    ctx.register_module(DummyModule())

    app = create_app(cfg, ctx)
    if app is None:
        return

    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["modules"]["total"] == 1
    assert data["modules"]["healthy"] == 1
