from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self
import tomllib
import mun.component  # noqa: F401 loaded for side-effect
from mun.entity import Entity
from mun.register import COMPONENTS

if TYPE_CHECKING:
    from mun.component import Component, Context

logger = logging.getLogger(__name__)


@dataclass
class ComponentSpec:
    name: str
    cls: type[Component]
    args: dict[str, Any]


@dataclass
class EntitySpec:
    name: str
    path: Path
    components: list[ComponentSpec]
    depends_on: list[EntitySpec]


@dataclass
class Registry:
    entities: dict[str, EntitySpec]
    components: dict[str, type[Component]] = field(default_factory=lambda: COMPONENTS)

    @classmethod
    def from_dirs(cls: type[Self], *, entity_dirs: set[Path]) -> Self:
        entities: dict[str, EntitySpec] = {}
        for dir in entity_dirs:
            if not dir.exists():
                logger.warn(f"Entity directory '{dir}' does not exist")
                continue

            logger.debug(f"Searching '{dir}' for entities")
            loaded_entities = _entities_in_dir(dir)

            for loaded_name, loaded_entity in loaded_entities.items():
                if loaded_name in entities:
                    _raise_entity_collision(entities[loaded_name], loaded_entity)

            entities.update(loaded_entities)

        return cls(entities=entities)

    def instantiate_entity(self, name: str, ctx: Context) -> Entity:
        entity_spec = self.entities[name]
        return Entity(
            name=entity_spec.name,
            path=entity_spec.path,
            components=[
                spec.cls(ctx=ctx, **spec.args) for spec in entity_spec.components
            ],
        )


def _entities_in_dir(dir: Path) -> dict[str, EntitySpec]:
    entities: dict[str, EntitySpec] = {}
    paths = (path for path in dir.iterdir() if path.name.endswith(".toml"))
    for path in paths:
        with path.open("rb") as fp:
            doc = tomllib.load(fp)

        name, loaded_entity = _entity_in_doc(doc=doc, path=path)
        if name in entities:
            _raise_entity_collision(entities[name], loaded_entity)

        entities[name] = loaded_entity

    return entities


def _entity_in_doc(*, doc: dict[str, Any], path: Path) -> tuple[str, EntitySpec]:
    assert path.name.endswith(".toml")
    name = doc.get("name", path.name[0 : -(len(path.suffix))])
    return (
        name,
        EntitySpec(
            name=name,
            path=path,
            components=_components_in_doc(doc),
            depends_on=doc.get("depends_on", []),
        ),
    )


def _components_in_doc(doc: dict[str, Any]) -> list[ComponentSpec]:
    components = []
    for name, args in doc.items():
        if not isinstance(args, dict):
            continue
        if (cls := COMPONENTS.get(str(name))) is None:
            raise ValueError(f"No component defined for '{name}'")
        components.append(
            ComponentSpec(
                name=name,
                cls=cls,
                args=args,
            )
        )
    return components


def _raise_entity_collision(ent1: EntitySpec, ent2: EntitySpec) -> None:
    assert ent1.name == ent2.name
    error_msg = (
        f"Two entities with name {ent1.name}" f"\n\t{ent1.path}" f"\n\t{ent2.path}"
    )
    raise KeyError(error_msg)
