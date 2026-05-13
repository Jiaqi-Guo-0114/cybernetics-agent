"""ConfigWatcher 最终补充测试"""
import json
import sys
import time

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.config_watcher import ConfigWatcher


class TestConfigWatcherFinal:
    def test_watch_and_stop(self, tmp_path):
        path = tmp_path / "cfg.json"
        path.write_text(json.dumps({"test": 1}))
        cw = ConfigWatcher(str(path), lambda cfg: None)
        time.sleep(0.01)
        cw.stop()
