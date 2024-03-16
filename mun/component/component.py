from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass
class Context:
    pwd: Path
    project_root: Path


class Component(Protocol):
    def __init__(self, *, ctx: Context, **kwargs: Any) -> None: ...
    async def start(self, *, ctx: Context) -> None: ...
    async def run(self, *, ctx: Context) -> None: ...
    async def stop(self, *, ctx: Context) -> None: ...
    async def reset(self, *, ctx: Context) -> None: ...
