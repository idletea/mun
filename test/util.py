from __future__ import annotations

import inspect


def members(cls: type) -> set[str]:
    return {
        member for member, _ in inspect.getmembers(cls) if not member.startswith("_")
    }
