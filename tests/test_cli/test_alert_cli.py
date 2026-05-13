"""
Alert CLI 命令测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.cli.alert_cmd import run_alert_status, run_alert_test
from cybernetics_agent.cli.main import create_parser


def test_alert_parser():
    """Alert 子命令解析正确。"""
    parser = create_parser()
    parsed = parser.parse_args(["alert", "status"])
    assert parsed.command == "alert"
    assert parsed.alert_command == "status"


def test_alert_status_no_config():
    """Status 命令在无配置时正确处理。"""
    class FakeParsed:
        config = "/tmp/nonexistent_cybernetics.json"
    assert run_alert_status(FakeParsed()) == 0


def test_alert_test_no_config():
    """Test 命令在无配置时正确处理。"""
    class FakeParsed:
        config = "/tmp/nonexistent_cybernetics.json"
        channel = None
    assert run_alert_test(FakeParsed()) == 0
