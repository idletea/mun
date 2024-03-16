from __future__ import annotations

import os
from pathlib import Path
from typing import Callable
import pytest

ROOT_INDICATORS_CONFIG = """
project_root_indicators = [".custom", ".git"]
"""


@pytest.fixture
def env(mocker):
    def inner(**kwargs):
        mocker.patch.dict(os.environ, kwargs)

    return inner


@pytest.fixture
def make_config_file(fs) -> Callable[[str], None]:
    def inner(contents: str) -> None:
        home = Path("~").expanduser()
        fs.create_file(home / ".config/mun/config.toml", contents=contents)

    return inner
