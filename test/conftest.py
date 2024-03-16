from __future__ import annotations

import os
from pathlib import Path
from typing import Callable
import pytest
from mun.component import Context
from mun.config import Config

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


@pytest.fixture
def config() -> Config:
    return Config.find_or_default()


@pytest.fixture
def ctx(config: Config, tmp_path: Path) -> Context:
    root_dir = tmp_path / "root"
    mun_dir = root_dir / ".mun"
    mun_dir.mkdir(parents=True)
    os.chdir(root_dir)
    return Context(
        project_root=config.project_root,
        pwd=Path.cwd(),
    )
