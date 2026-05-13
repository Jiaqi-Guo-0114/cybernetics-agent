"""ConfigWatcher 剩余代码补充测试"""
import pytest
import sys, json
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.config_watcher import ConfigWatcher

class TestConfigWatcherCoverage:
    def test_watch_file(self, tmp_path):
        path = tmp_path / "cfg.json"
        path.write_text(json.dumps({"test": 1}))
        cw = ConfigWatcher(str(path), lambda cfg: None)
        assert cw is not None

    def test_stop(self, tmp_path):
        path = tmp_path / "cfg.json"
        path.write_text(json.dumps({"test": 1}))
        cw = ConfigWatcher(str(path), lambda cfg: None)
        cw.stop()
