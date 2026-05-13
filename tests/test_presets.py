"""Presets 最终补充"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.presets import get_preset, list_presets


class TestPresetsFinal:
    def test_list(self):
        presets = list_presets()
        assert isinstance(presets, list)

    def test_get_each(self):
        for name in list_presets():
            p = get_preset(name)
            assert isinstance(p, dict)
