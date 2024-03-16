from __future__ import annotations

import os
from pathlib import Path
from typing import Callable
import pytest
from mun.component import Context
from mun.config import ENV_CONFIG_PATH, Config

ROOT_INDICATORS_CONFIG = """
project_root_indicators = [".custom", ".git"]
"""


@pytest.fixture
def env(mocker):
    def inner(**kwargs):
        mocker.patch.dict(os.environ, kwargs)

    return inner


@pytest.fixture
def config_file(tmp_path, env) -> Callable[[str], None]:
    def inner(contents: str) -> None:
        dir = tmp_path / "__mun_test"
        dir.mkdir()
        file = dir / "config.toml"
        env(**{ENV_CONFIG_PATH: str(file)})
        with file.open("w+") as fp:
            fp.write(contents)

    return inner


@pytest.fixture
def config(config_file) -> Config:
    config_file("")
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
