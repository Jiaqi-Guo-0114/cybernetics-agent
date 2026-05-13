"""
Dashboard 测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig, CyberneticsContext


def test_dashboard_fastapi_app_creation():
    """FastAPI 应用能正确创建。"""
    try:
        from cybernetics_agent.cli.dashboard_fastapi import create_app, HAS_FASTAPI
    except ImportError:
        return  # 可选依赖未安装

    if not HAS_FASTAPI:
        return

    config = CyberneticsConfig(project_name="test")
    ctx = CyberneticsContext(config)
    app = create_app(config, ctx)
    assert app is not None


def test_dashboard_html_generation():
    """Dashboard HTML 能正确生成。"""
    from cybernetics_agent.cli.dashboard_fastapi import _generate_dashboard_html

    config = CyberneticsConfig(project_name="test")
    ctx = CyberneticsContext(config)
    html = _generate_dashboard_html(config, ctx)
    assert "Cybernetics Agent" in html
    assert "test" in html
    assert "EventSource" in html  # SSE
