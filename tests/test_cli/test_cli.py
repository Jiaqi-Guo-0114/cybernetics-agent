"""
CLI 工具的 pytest 测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from cybernetics_agent.cli.main import create_parser, main


def test_parser_help():
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])


def test_init_command():
    import os
    # 先删除可能存在的文件，避免交互式提示
    if os.path.exists("/tmp/test_init.json"):
        os.remove("/tmp/test_init.json")
    result = main(["init", "-o", "/tmp/test_init.json"])
    assert result == 0
    assert Path("/tmp/test_init.json").exists()


def test_validate_valid_config():
    import os
    # 先创建配置文件
    if os.path.exists("/tmp/test_validate.json"):
        os.remove("/tmp/test_validate.json")
    main(["init", "-o", "/tmp/test_validate.json"])
    result = main(["validate", "/tmp/test_validate.json"])
    assert result == 0


def test_validate_invalid_file():
    result = main(["validate", "/nonexistent/file.json"])
    assert result == 1
