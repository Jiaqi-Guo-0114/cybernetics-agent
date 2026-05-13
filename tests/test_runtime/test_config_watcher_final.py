"""ConfigWatcher 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.config_watcher import ConfigWatcher

class TestConfigWatcherFinal:
    def test_init(self):
        cw = ConfigWatcher("/dev/null", lambda x: None)
        assert cw is not None
