from __future__ import annotations

import re


def camel_case(s: str) -> str:
    return re.sub(
        "([a-z0-9])([A-Z])",
        r"\1_\2",
        re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s),
    ).lower()
