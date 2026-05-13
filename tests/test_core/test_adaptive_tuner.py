"""
自适应调优测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.core.adaptive_tuner import AdaptiveTuner


def test_auto_tune_numeric():
    """数值型参数自动调整。"""
    config = {
        "enabled": True,
        "learning_rate": 0.5,
        "parameters": [
            {"name": "max_papers", "base": 10, "min": 3, "max": 50},
        ],
    }
    tuner = AdaptiveTuner(config, None)

    # 模拟高成功率
    tuner._tool_scores = {"search": 0.9, "download": 0.9}
    changes = tuner.auto_tune()

    assert "max_papers" in changes
    assert changes["max_papers"]["new"] > changes["max_papers"]["old"]


def test_auto_tune_low_score():
    """低成功率时降低参数。"""
    import random
    random.seed(42)  # 固定种子避免探索随机性

    config = {
        "enabled": True,
        "learning_rate": 0.5,
        "parameters": [
            {"name": "max_papers", "base": 10, "min": 3, "max": 50},
        ],
    }
    tuner = AdaptiveTuner(config, None)

    # 模拟低成功率
    tuner._tool_scores = {"search": 0.1, "download": 0.2}
    changes = tuner.auto_tune()

    assert "max_papers" in changes
    assert changes["max_papers"]["new"] < changes["max_papers"]["old"]


def test_auto_tune_option():
    """选项型参数自动调整。"""
    config = {
        "enabled": True,
        "learning_rate": 0.5,
        "parameters": [
            {"name": "depth", "base": "normal", "options": ["shallow", "normal", "deep"]},
        ],
    }
    tuner = AdaptiveTuner(config, None)

    # 高成功率应该向 "deep" 移动
    tuner._tool_scores = {"search": 0.9}
    changes = tuner.auto_tune()

    assert "depth" in changes
    assert changes["depth"]["new"] == "deep"


def test_suggest_parameters():
    """推荐参数不应用。"""
    config = {
        "enabled": True,
        "learning_rate": 0.5,
        "parameters": [
            {"name": "max_papers", "base": 10, "min": 3, "max": 50},
        ],
    }
    tuner = AdaptiveTuner(config, None)
    tuner._tool_scores = {"search": 0.9}

    suggestions = tuner.suggest_parameters()
    assert "max_papers" in suggestions
    assert "suggested" in suggestions["max_papers"]
    # suggest 不应该改变当前值
    assert tuner.get_parameter("max_papers") == 10


def test_confidence_increases_with_samples():
    """置信度随样本增加。"""
    config = {"enabled": True, "learning_rate": 0.3, "parameters": []}
    tuner = AdaptiveTuner(config, None)

    c0 = tuner._estimate_confidence("x")
    assert c0 == 0.0

    for i in range(10):
        tuner._tool_scores[f"tool_{i}"] = 0.5

    c1 = tuner._estimate_confidence("x")
    assert c1 > c0
    assert c1 <= 1.0
