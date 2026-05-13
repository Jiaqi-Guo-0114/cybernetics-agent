"""Presets 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.presets import list_presets, get_preset

class TestPresetsEdgeCases:
    def test_list_presets(self):
        presets = list_presets()
        assert isinstance(presets, list)
        assert len(presets) > 0

    def test_get_each_preset(self):
        for name in list_presets():
            preset = get_preset(name)
            assert isinstance(preset, dict)
            assert len(preset) > 0

    def test_get_invalid_preset(self):
        with pytest.raises(KeyError):
            get_preset("nonexistent")
