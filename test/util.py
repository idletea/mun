from __future__ import annotations

import inspect
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def chdir(to: Path | str) -> Iterator[None]:
    cwd = Path.cwd()
    os.chdir(to)
    yield None
    os.chdir(cwd)


def members(cls: type) -> set[str]:
    return {
        member for member, _ in inspect.getmembers(cls) if not member.startswith("_")
    }
