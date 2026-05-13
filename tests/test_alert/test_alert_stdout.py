"""
标准输出告警渠道测试。
"""

import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.alert.channels import StdoutChannel
from cybernetics_agent.alert.core import AlertEvent


def test_stdout_channel_send():
    """StdoutChannel 能正确输出告警。"""
    stream = StringIO()
    ch = StdoutChannel(stream=stream)
    evt = AlertEvent(
        rule_name="test",
        severity="error",
        message="something wrong",
        metric_name="error_rate",
        metric_value=0.8,
    )
    result = ch.send(evt)
    assert result is True
    output = stream.getvalue()
    assert "告警:ERROR" in output
    assert "test" in output
    assert "something wrong" in output
    assert "error_rate=0.8" in output


def test_stdout_channel_health_check():
    """StdoutChannel 健康检查始终通过。"""
    ch = StdoutChannel()
    assert ch.health_check() is True
