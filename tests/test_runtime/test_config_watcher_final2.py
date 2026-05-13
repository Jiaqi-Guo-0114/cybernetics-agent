"""ConfigWatcher 最终补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.config_watcher import ConfigWatcher


class TestConfigWatcherFinal2:
    def test_watch_nonexistent(self):
        cw = ConfigWatcher("/nonexistent/file.json", lambda cfg: None)
        cw.stop()
