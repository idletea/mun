from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, cast
from mun.util import camel_case

if TYPE_CHECKING:
    from mun.component import Component, Context


COMPONENTS: dict[str, Component] = {}


class DefaultComponent:
    def __init__(self, **kwargs: Any) -> None:
        pass

    async def start(self, *, mun: Context) -> None:
        raise NotImplementedError()

    async def run(self, *, mun: Context) -> None:
        raise NotImplementedError()

    async def stop(self, *, mun: Context) -> None:
        raise NotImplementedError()

    async def reset(self, *, mun: Context) -> None:
        raise NotImplementedError()


def component(*, with_defaults: bool = False) -> Callable[[type], type]:
    """Make a component known to the components registry.

    The `with_defaults` argument will implicitly add a no-op base class as a
    convenience for components that only wish to implement a subset of handlers.
    """

    def inner(component: type) -> type:
        cls = component
        if with_defaults:
            cls = type(
                f"Defaulted{component.__name__}",
                (component, DefaultComponent),
                {},
            )
            cls.__doc__ = component.__doc__

        name = camel_case(component.__name__)
        COMPONENTS[name] = cast("Component", cls)

        return component

    return inner
