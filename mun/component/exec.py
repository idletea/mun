from __future__ import annotations

import asyncio
import io
import logging
from functools import partial
from pathlib import Path
from typing import Annotated, Any
from pydantic import BaseModel, Field, conlist
from mun import register
from mun.component import Context

logger = logging.getLogger(__name__)


class Args(BaseModel):
    cwd: Path = Path()  # relative to project root
    args: Annotated[list[str], conlist(str, min_length=1)]
    stdout: Path = Field(default_factory=partial(Path, "/dev/stdout"))
    stderr: Path = Field(default_factory=partial(Path, "/dev/stderr"))


@register.component(with_defaults=True)
class Exec:
    """Execute arbitrary processes."""

    proc: asyncio.subprocess.Process | None = None
    cwd: Path
    args: Args
    stdout: io.BufferedWriter
    stderr: io.BufferedWriter

    def __init__(self, *, ctx: Context, **kwargs: Any) -> None:
        self.args = Args(**kwargs)

        self.cwd = (ctx.project_root / self.args.cwd).resolve()
        self.stdout = self.args.stdout.open("wb")
        self.stderr = self.args.stderr.open("wb")

    async def start(self, *, ctx: Context) -> None:  # noqa: ARG002
        self.proc = await asyncio.create_subprocess_exec(
            self.args.args[0],
            *self.args.args[1:],
            stdout=self.stdout,
            stderr=self.stderr,
            cwd=self.cwd,
        )

    async def run(self, *, ctc: Context) -> None:  # noqa: ARG002
        assert self.proc
        status = await self.proc.wait()
        if status == 0:
            logger.debug(f"{self.args.args} exited succesfully")
        else:
            logger.warn(f"{self.args.args} exited with status {status}")
