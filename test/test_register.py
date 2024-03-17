from __future__ import annotations

from typing import Any
import pytest
import util
from mun import register
from mun.component import Context


@register.component(with_defaults=True)
class Defaulted:
    def __init__(self, *, ctx: Context, **kwargs: Any) -> None: ...
    async def start(self, *, ctx: Context) -> None:  # noqa: ARG002
        raise FileNotFoundError("test error")


@register.component
class NotDefaulted:
    def __init__(self, *, ctx: Context, **kwargs: Any) -> None: ...
    async def start(self, *, ctx: Context) -> None: ...
    async def run(self, *, ctx: Context) -> None: ...
    async def stop(self, *, ctx: Context) -> None: ...
    async def reset(self, *, ctx: Context) -> None: ...


def test_register_component() -> None:
    assert register.COMPONENTS["defaulted"]
    assert register.COMPONENTS["not_defaulted"]


@pytest.mark.anyio
async def test_with_defaults_simple(ctx) -> None:
    defaulted = register.COMPONENTS["defaulted"](ctx=ctx)

    # defaulting doesn't override defined methods
    with pytest.raises(FileNotFoundError):
        await defaulted.start(ctx=ctx)

    implemented = util.members(Defaulted)
    default_impls = util.members(register.COMPONENTS["defaulted"]) - implemented
    assert len(default_impls)

    for member in default_impls:
        with pytest.raises(NotImplementedError):
            await getattr(defaulted, member)(ctx=ctx)
