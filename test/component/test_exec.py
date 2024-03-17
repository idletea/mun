from __future__ import annotations

import logging
from pathlib import Path
import pytest
from mun.component import Context
from mun.component.exec import Exec


@pytest.mark.anyio
async def test_arg_cwd(
    ctx: Context,
    tmp_path: Path,
) -> None:
    for path in ["", "foo", "foo/bar"]:
        cwd = tmp_path / path
        cwd.mkdir(parents=True, exist_ok=True)

        exec = Exec(ctx=ctx, args=["touch", "new-file"], cwd=str(cwd))
        await exec.start(ctx=ctx)
        await exec.run(ctx=ctx)

        assert (cwd / "new-file").is_file()


@pytest.mark.anyio
async def test_arg_env_is_set(
    ctx: Context,
    tmp_path: Path,
) -> None:
    stdout = tmp_path / "__stdout"
    exec = Exec(
        ctx=ctx, args=["bash", "-c", "printf $FOO"], stdout=stdout, env={"FOO": "BAR"}
    )

    await exec.start(ctx=ctx)
    await exec.run(ctx=ctx)

    with stdout.open("r") as fp:
        assert fp.readline() == "BAR"


@pytest.mark.anyio
async def test_reports_status(ctx: Context, caplog: pytest.LogCaptureFixture) -> None:
    exec = Exec(ctx=ctx, args=["false"])

    await exec.start(ctx=ctx)
    caplog.clear()
    await exec.run(ctx=ctx)
    assert any(record.levelno > logging.INFO for record in caplog.records)
