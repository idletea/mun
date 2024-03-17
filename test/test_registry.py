from __future__ import annotations

from pathlib import Path
import pytest
from mun import register
from mun.config import Config
from mun.registry import Registry


@register.component(with_defaults=True)
class TestComp1: ...


@register.component(with_defaults=True)
class TestComp2: ...


def test_entity_discovery(config: Config, project_root: Path, sibling_roots):
    with (project_root / ".mun/entities/ent1.toml").open("w+") as fp:
        fp.write("""[test_comp1]""")
    with (project_root / ".mun/entities/ent2.toml").open("w+") as fp:
        fp.write("""[test_comp1]\n[test_comp2]""")
    with (sibling_roots[0] / ".mun/entities/ent3.toml").open("w+") as fp:
        fp.write("""""")
    reg = Registry.from_dirs(entity_dirs=config.entity_dirs)

    assert (ent1 := reg.entities["ent1"])  # noqa: RUF018
    assert ent1.path == project_root / ".mun/entities/ent1.toml"
    assert (ent2 := reg.entities["ent2"])  # noqa: RUF018
    assert ent2.path == project_root / ".mun/entities/ent2.toml"
    assert (ent3 := reg.entities["ent3"])  # noqa: RUF018
    assert ent3.path == sibling_roots[0] / ".mun/entities/ent3.toml"


def test_entity_collision_by_file_name_fails(
    config: Config, project_root: Path, sibling_roots: list[Path]
):
    with (project_root / ".mun/entities/ent1.toml").open("w+") as fp:
        fp.write("""[test_comp1]""")
    with (sibling_roots[0] / ".mun/entities/ent1.toml").open("w+") as fp:
        fp.write("""[test_comp1]\n[test_comp2]""")

    with pytest.raises(KeyError):
        Registry.from_dirs(entity_dirs=config.entity_dirs)


def test_entity_collision_by_explicit_name_fails(
    config: Config, project_root: Path
) -> None:
    with (project_root / ".mun/entities/ent1.toml").open("w+") as fp:
        fp.write("""[test_comp1]""")
    with (project_root / ".mun/entities/ent2.toml").open("w+") as fp:
        fp.write("""name = "ent1"\n[test_comp1]""")

    with pytest.raises(KeyError):
        Registry.from_dirs(entity_dirs=config.entity_dirs)


def test_component_discovery_in_entities(config, project_root, sibling_roots) -> None:
    with (project_root / ".mun/entities/ent1.toml").open("w+") as fp:
        fp.write("""[test_comp1]""")
    with (sibling_roots[0] / ".mun/entities/ent2.toml").open("w+") as fp:
        fp.write("""[test_comp1]\n[test_comp2]""")
    reg = Registry.from_dirs(entity_dirs=config.entity_dirs)

    assert (comp1 := reg.entities["ent1"].components)  # noqa: RUF018
    assert [component.name for component in comp1] == ["test_comp1"]
    assert (comp2 := reg.entities["ent2"].components)  # noqa: RUF018
    assert [component.name for component in comp2] == ["test_comp1", "test_comp2"]


def test_component_discovery_maintain_order(config, project_root) -> None:
    with (project_root / ".mun/entities/ent2.toml").open("w+") as fp:
        fp.write("""[test_comp1]\n[test_comp2]""")
    with (project_root / ".mun/entities/ent3.toml").open("w+") as fp:
        fp.write("""[test_comp2]\n[test_comp1]""")
    reg = Registry.from_dirs(entity_dirs=config.entity_dirs)

    assert (comp2 := reg.entities["ent2"].components)  # noqa: RUF018
    assert [component.name for component in comp2] == ["test_comp1", "test_comp2"]
    assert (comp3 := reg.entities["ent3"].components)  # noqa: RUF018
    assert [component.name for component in comp3] == ["test_comp2", "test_comp1"]


def test_entity_can_have_no_components(config, project_root) -> None:
    with (project_root / ".mun/entities/ent1.toml").open("w+") as fp:
        fp.write("""""")
    reg = Registry.from_dirs(entity_dirs=config.entity_dirs)

    assert not reg.entities["ent1"].components
