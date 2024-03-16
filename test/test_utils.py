from __future__ import annotations

import pytest
from mun.util import camel_case


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Foo", "foo"),
        ("FooBar", "foo_bar"),
        ("FooBarBaz", "foo_bar_baz"),
        ("FOOBar", "foo_bar"),
    ],
)
def test_camel_case(input: str, expected: str):
    assert camel_case(input) == expected
