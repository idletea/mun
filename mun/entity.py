from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path
import anyio
from mun.component import Component, Context


@dataclass
class Entity:
    name: str
    path: Path
    components: list[Component]

    async def start(self, *, ctx: Context) -> None:
        for component in self.components:
            await component.start(ctx=ctx)

    async def run(self, *, ctx: Context) -> None:
        async with anyio.create_task_group() as tg:
            for component in self.components:
                tg.start_soon(partial(component.run, ctx=ctx))

    async def stop(self, *, ctx: Context) -> None:
        for component in reversed(self.components):
            await component.stop(ctx=ctx)

    async def reset(self, *, ctx: Context) -> None:
        for component in self.components:
            await component.reset(ctx=ctx)
