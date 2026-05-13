"""Tests for alert.channels.base — AlertChannel abstract base class."""

from __future__ import annotations

import pytest

from cybernetics_agent.alert.channels.base import AlertChannel
from cybernetics_agent.alert.core import AlertEvent


class TestAlertChannel:
    """AlertChannel 抽象基类测试。"""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            AlertChannel()

    def test_subclass_must_implement_send(self):
        class Partial(AlertChannel):
            name = "partial"

        with pytest.raises(TypeError):
            Partial()

    def test_valid_subclass_send(self):
        class DummyChannel(AlertChannel):
            name = "dummy"

            def send(self, event: AlertEvent) -> bool:
                return True

        ch = DummyChannel()
        event = AlertEvent(rule_name="test", severity="warning", message="hello")
        assert ch.send(event) is True
        assert ch.name == "dummy"

    def test_health_check_default_true(self):
        class DummyChannel(AlertChannel):
            name = "dummy"

            def send(self, event: AlertEvent) -> bool:
                return True

        ch = DummyChannel()
        assert ch.health_check() is True

    def test_health_check_override(self):
        class SickChannel(AlertChannel):
            name = "sick"

            def send(self, event: AlertEvent) -> bool:
                return False

            def health_check(self) -> bool:
                return False

        ch = SickChannel()
        assert ch.health_check() is False

    def test_send_receives_alert_event(self):
        class CaptureChannel(AlertChannel):
            name = "capture"
            last_event = None

            def send(self, event: AlertEvent) -> bool:
                self.last_event = event
                return True

        ch = CaptureChannel()
        event = AlertEvent(
            rule_name="cpu_high",
            severity="critical",
            message="CPU > 90%",
            metric_name="cpu",
            metric_value=95.0,
            labels={"host": "srv-01"},
        )
        assert ch.send(event) is True
        assert ch.last_event is event
        assert ch.last_event.rule_name == "cpu_high"
        assert ch.last_event.metric_value == 95.0

    def test_send_returns_false_on_failure(self):
        class FailingChannel(AlertChannel):
            name = "failing"

            def send(self, event: AlertEvent) -> bool:
                return False

        ch = FailingChannel()
        event = AlertEvent(rule_name="fail", message="boom")
        assert ch.send(event) is False
