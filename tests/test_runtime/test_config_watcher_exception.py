"""ConfigWatcher 异常路径"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.config_watcher import ConfigWatcher

class TestConfigWatcherException:
    def test_watch_missing_file(self):
        cw = ConfigWatcher("/nonexistent/file.json", lambda cfg: None)
        cw.stop()
