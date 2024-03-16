from __future__ import annotations

import glob
import itertools
import logging
import os
import sys
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path, PurePath
from typing import Self
import tomllib
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
ENV_CONFIG_PATH: str = "MUN_CONFIG"


def default_config_search() -> Path | None:
    if env := os.environ.get(ENV_CONFIG_PATH):
        path = Path(env).expanduser()
        if path.exists():
            return Path(env)
        raise ValueError(f"{ENV_CONFIG_PATH} is not a file")
    default = Path("~/.config/mun/config.toml").expanduser()
    return default if default.exists() else None


class Opts(BaseModel):
    """Configuration schema expected for a configuration file."""

    # project root determinant - the first directory found containing
    # a child with one of these names is used as the project root
    project_root_indicators: list[Path] = Field(default_factory=lambda: [Path(".mun")])

    # sibling project patterns - these values are expanded using `Path.glob` if relative
    # or `glob.glob` if absolute. If a result matches a directory that also contains a
    # project_root_indicator, it will be added to the list of sibling project roots
    sibling_project_patterns: list[str] = Field(default_factory=lambda: ["../*"])

    # directories to search for entities - relative to the project roots
    entity_dir_patterns: list[Path] = Field(
        default_factory=lambda: [Path(".mun/entities")]
    )


@dataclass
class Config:
    opts: Opts

    @classmethod
    def find_or_default(cls: type[Self]) -> Self:
        overrides = {}
        if path := default_config_search():
            with path.open("rb") as fp:
                logging.info(f"Using config file {path}")
                overrides = tomllib.load(fp)
        opts = Opts(**overrides)

        return cls(opts=opts)

    @cached_property
    def project_root(self) -> Path:
        def has_indicator(pwd: Path) -> bool:
            return any(
                (pwd / indicator).exists()
                for indicator in self.opts.project_root_indicators
            )

        root = Path("/")
        pwd = Path().resolve()

        while pwd != root:
            if has_indicator(pwd):
                return pwd
            pwd = pwd.parent

        if has_indicator(root):
            return root

        logger.error(f"Could not locate a project root from {Path().resolve()}")
        sys.exit(1)

    @cached_property
    def sibling_roots(self) -> set[Path]:
        prospects: set[Path] = set()
        for pattern in self.opts.sibling_project_patterns:
            if PurePath(pattern).is_absolute():
                prospects |= self._absolute_sibling_pattern_expansions(pattern)
            else:
                prospects |= self._relative_sibling_pattern_expansions(pattern)

        checks = itertools.product(prospects, self.opts.project_root_indicators)
        return {
            path.resolve()
            for (path, indicator) in checks
            if (path / indicator).exists()
        }

    @cached_property
    def roots(self) -> set[Path]:
        return {self.project_root, *self.sibling_roots}

    @cached_property
    def entity_dirs(self) -> set[Path]:
        checks = itertools.product(self.roots, self.opts.entity_dir_patterns)
        return {
            (root / pattern).resolve()
            for (root, pattern) in checks
            if (root / pattern).is_dir()
        }

    def _absolute_sibling_pattern_expansions(self, pattern: str) -> set[Path]:
        globbed = (Path(p).resolve() for p in glob.glob(pattern))  # noqa: PTH207
        return {path for path in globbed if path != self.project_root}

    def _relative_sibling_pattern_expansions(self, pattern: str) -> set[Path]:
        return {
            path
            for path in self.project_root.glob(pattern)
            if path.resolve() != self.project_root
        }
