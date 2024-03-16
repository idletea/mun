from __future__ import annotations

from typing import Any, Protocol


class Context: ...


class Component(Protocol):
    def __init__(self, **kwargs: Any) -> None: ...
    async def start(self, *, mun: Context) -> None: ...
    async def run(self, *, mun: Context) -> None: ...
    async def stop(self, *, mun: Context) -> None: ...
    async def reset(self, *, mun: Context) -> None: ...