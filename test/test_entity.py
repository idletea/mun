from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Any
import anyio
import pytest
from mun import register
from mun.component import Context
from mun.config import Config
from mun.registry import Registry


@register.component(with_defaults=True)
class SequenceTestA:
    event: anyio.Event

    def __init__(self, *, ctx: Context, **kwargs: Any) -> None:  # noqa: ARG002
        self.event = kwargs["event"]
        self.past_events = kwargs["past_events"]
        self.future_events = kwargs["future_events"]

    async def start(self, *, ctx: Context) -> None:  # noqa: ARG002
        self._assert()

    async def stop(self, *, ctx: Context) -> None:  # noqa: ARG002
        self._assert()

    def _assert(self) -> None:
        for past_event in self.past_events:
            assert past_event.is_set()
        self.event.set()
        for future_event in self.future_events:
            assert not future_event.is_set()


@register.component(with_defaults=True)
class SequenceTestB(SequenceTestA): ...


@register.component(with_defaults=True)
class SequenceTestC(SequenceTestA): ...


@register.component(with_defaults=True)
class SequenceTestD(SequenceTestA): ...


@pytest.mark.anyio
async def test_entity_start_sequencing(
    ctx: Context, project_root: Path, config: Config
):
    """Test that starting an entity starts all components in sequence."""
    with (project_root / ".mun/entities/ent.toml").open("w+") as fp:
        fp.write("""
            [sequence_test_a]
            [sequence_test_b]
            [sequence_test_c]
            [sequence_test_d]
        """)
    reg = Registry.from_dirs(entity_dirs=config.entity_dirs)
    entity_spec = reg.entities["ent"]

    events = [anyio.Event() for _ in range(4)]
    for i in range(4):
        spec = entity_spec.components[i]
        spec.args["past_events"] = events[0:i]
        spec.args["event"] = events[i]
        spec.args["future_events"] = events[i + 1 :]

    entity = reg.instantiate_entity("ent", ctx=ctx)

    async with anyio.create_task_group() as tg:
        assert not any(event for event in events if event.is_set())
        tg.start_soon(partial(entity.start, ctx=ctx))


@pytest.mark.anyio
async def test_entity_stop_sequencing(ctx: Context, project_root: Path, config: Config):
    """Test that starting an entity stops all components in reverse sequence."""
    with (project_root / ".mun/entities/ent.toml").open("w+") as fp:
        fp.write("""
            [sequence_test_a]
            [sequence_test_b]
            [sequence_test_c]
            [sequence_test_d]
        """)
    reg = Registry.from_dirs(entity_dirs=config.entity_dirs)
    entity_spec = reg.entities["ent"]

    events = [anyio.Event() for _ in range(4)]
    for i in range(4):
        spec = entity_spec.components[i]
        spec.args["past_events"] = events[i + 1 :]
        spec.args["event"] = events[i]
        spec.args["future_events"] = events[0:i]

    entity = reg.instantiate_entity("ent", ctx=ctx)

    async with anyio.create_task_group() as tg:
        assert not any(event for event in events if event.is_set())
        tg.start_soon(partial(entity.stop, ctx=ctx))
