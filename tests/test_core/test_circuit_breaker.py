"""CircuitBreaker 测试"""
import pytest
import time
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.circuit_breaker import CircuitBreaker

class TestCircuitBreaker:
    def test_init_defaults(self):
        cb = CircuitBreaker()
        assert cb.can_execute() is True
        status = cb.get_status()
        assert status["state"] == "closed"

    def test_record_success(self):
        cb = CircuitBreaker()
        cb.record_success()
        assert cb.can_execute() is True

    def test_record_failure_opens(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.can_execute() is True
        cb.record_failure()
        assert cb.can_execute() is False
        status = cb.get_status()
        assert status["state"] == "open"

    def test_recovery(self):
        import time
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        cb.record_failure()
        assert cb.can_execute() is False
        time.sleep(0.15)
        assert cb.can_execute() is True
        status = cb.get_status()
        assert status["state"] in ("half_open", "closed")

    def test_half_open_max_calls(self):
        import time
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1, half_open_max_calls=2)
        cb.record_failure()
        time.sleep(0.15)
        assert cb.can_execute() is True
        cb.record_success()
        assert cb.can_execute() is True
        cb.record_success()
        assert cb.can_execute() is True

    def test_half_open_success_closes(self):
        import time
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1, half_open_max_calls=2)
        cb.record_failure()
        assert cb.can_execute() is False
        time.sleep(0.15)
        assert cb.can_execute() is True  # half_open
        cb.record_success()
        cb.record_success()
        assert cb.can_execute() is True  # 应该已经关闭
