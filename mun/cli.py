from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from typing import Iterator
import click
import rich
from rich.logging import RichHandler
from mun.config import Config
from mun.registry import Registry

logger = logging.getLogger(__name__)


def main() -> None:
    try:
        cli()
    except Exception:
        logger.exception("Fatal error")
        sys.exit(1)


def config_logging(*, verbose: bool, quiet: bool) -> None:
    class MunDebugOnlyFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if record.levelno < logging.INFO:
                return record.name.startswith("mun.")
            return True

    match (verbose, quiet):
        case (True, True):
            raise ValueError("both verbose and quiet output requested")
        case (True, False):
            level = logging.DEBUG
        case (False, True):
            level = logging.WARNING
        case (False, False):
            level = logging.INFO

    handler = RichHandler()
    handler.addFilter(MunDebugOnlyFilter())
    logging.basicConfig(
        format="%(message)s",
        level=level,
        datefmt="[%X]",
        handlers=[handler],
    )


@dataclass
class ClickContext:
    config: Config
    registry: Registry


@click.group()
@click.option("--verbose", "-v", is_flag=True, default=False, help="Verbose output.")
@click.option("--quiet", "-q", is_flag=True, default=False, help="Avoid output.")
@click.pass_context
def cli(ctx: click.Context, *, verbose: bool, quiet: bool) -> None:
    config_logging(verbose=verbose, quiet=quiet)
    config = Config.find_or_default()
    registry = Registry.from_dirs(entity_dirs=config.entity_dirs)
    ctx.obj = ClickContext(config=config, registry=registry)


@cli.group()
@click.pass_context
def component(_ctx: click.Context) -> None: ...


@component.command(name="list")
@click.pass_context
def component_list(ctx: click.Context) -> None:
    registry: Registry = ctx.obj.registry
    _output_two_col_table(
        items=(
            (name, str(component.__doc__))
            for name, component in registry.components.items()
        ),
    )


@cli.group()
@click.pass_context
def entity(_ctx: click.Context) -> None: ...


@entity.command(name="list")
@click.pass_context
def entity_list(ctx: click.Context) -> None:
    registry: Registry = ctx.obj.registry
    _output_two_col_table(
        items=(
            (entity.name, str(entity.path)) for entity in registry.entities.values()
        ),
    )


def _output_two_col_table(
    *,
    items: Iterator[tuple[str, str]],
    styles: tuple[str, str] = ("bold", "bold magenta"),
) -> None:
    table = rich.table.Table(
        box=None, show_header=False, show_footer=False, pad_edge=False, highlight=True
    )
    table.add_column(style=styles[0])
    table.add_column(style=styles[1])
    for a, b in items:
        table.add_row(a, b)

    rich.console.Console().print(table)
