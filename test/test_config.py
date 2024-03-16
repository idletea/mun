from __future__ import annotations

import os
from pathlib import PosixPath
import pytest
from mun.config import Config
import util


def test_config_default():
    Config.find_or_default()


def test_config_from_default_file(config_file):
    config_file("""entity_dir_patterns = [".foo/entities"]""")
    assert Config.find_or_default().opts.entity_dir_patterns == [
        PosixPath(".foo/entities")
    ]


def test_default_project_root_discovery(tmp_path):
    (tmp_path / ".mun").mkdir(parents=True)
    (tmp_path / "foo/.foo").mkdir(parents=True)
    (tmp_path / "foo/bar/.mun").mkdir(parents=True)
    (tmp_path / "foo/bar/baz/foo/.foo").mkdir(parents=True)

    os.chdir(tmp_path)
    for cd_to, expect_root in [
        ("foo/bar/baz/foo", tmp_path / "foo/bar"),
        ("foo/bar", tmp_path / "foo/bar"),
        ("foo", tmp_path),
    ]:
        with util.chdir(cd_to):
            actual_root = Config.find_or_default().project_root
            assert str(actual_root) == str(expect_root)


def test_custom_project_root_discovery(tmp_path, config_file):
    config_file("""project_root_indicators = [".foo", ".git"]""")

    (tmp_path / "foo/bar/.git").mkdir(parents=True)
    (tmp_path / "foo/bar/baz/.foo").mkdir(parents=True)
    (tmp_path / "foo/bar/baz/foo/bar").mkdir(parents=True)

    os.chdir(tmp_path)
    for cd_to, expect_root in [
        ("foo/bar/baz", tmp_path / "foo/bar/baz"),
        ("foo/bar", tmp_path / "foo/bar"),
        ("foo/bar/baz/foo/bar", tmp_path / "foo/bar/baz"),
    ]:
        with util.chdir(cd_to):
            actual_root = Config.find_or_default().project_root
            assert str(actual_root) == str(expect_root)

    os.chdir("/tmp")
    with pytest.raises(SystemExit):
        _ = Config.find_or_default().project_root


def test_default_sibling_root_discovery(tmp_path):
    (tmp_path / "foo/root/.mun").mkdir(parents=True)
    (tmp_path / "foo/sib1/.mun").mkdir(parents=True)
    (tmp_path / "foo/sib2/.mun").mkdir(parents=True)
    (tmp_path / "foo/notsib/.not-mun").mkdir(parents=True)

    os.chdir(tmp_path / "foo/root")
    config = Config.find_or_default()
    assert sorted([str(path) for path in config.sibling_roots]) == [
        str(tmp_path / "foo/sib1"),
        str(tmp_path / "foo/sib2"),
    ]


def test_custom_sibling_root_discovery(tmp_path, config_file):
    (tmp_path / "proj/sib1/.mun").mkdir(parents=True)
    (tmp_path / "proj/sib2/.mun").mkdir(parents=True)
    (tmp_path / "proj/sib3/mun").mkdir(parents=True)
    (tmp_path / "proj/notme").mkdir(parents=True)
    (tmp_path / "foo/other/.mun").mkdir(parents=True)
    (tmp_path / "foo/notme").mkdir(parents=True)
    (tmp_path / "foo/root/.mun").mkdir(parents=True)

    os.chdir(tmp_path / "foo/root")
    absolute_proj = tmp_path / "proj"
    config_file(f"""sibling_project_patterns = ["{absolute_proj}/*", "../other"]""")
    assert sorted([str(path) for path in Config.find_or_default().sibling_roots]) == [
        str(tmp_path / "foo/other"),
        str(tmp_path / "proj/sib1"),
        str(tmp_path / "proj/sib2"),
    ]


def test_roots(tmp_path):
    (tmp_path / "foo/root/.mun").mkdir(parents=True)
    (tmp_path / "foo/sib1/.mun").mkdir(parents=True)
    (tmp_path / "foo/sib2/.mun").mkdir(parents=True)

    os.chdir(tmp_path / "foo/root")
    config = Config.find_or_default()
    assert sorted([str(path) for path in config.roots]) == [
        str(tmp_path / "foo/root"),
        str(tmp_path / "foo/sib1"),
        str(tmp_path / "foo/sib2"),
    ]


def test_default_entity_dir_discovery(tmp_path):
    (tmp_path / "foo/root/.mun/entities").mkdir(parents=True)
    (tmp_path / "foo/sib1/.mun/entities").mkdir(parents=True)
    (tmp_path / "foo/sib2/.mun/not-entities").mkdir(parents=True)
    (tmp_path / "foo/sib2/.mun/entities").touch()  # file, not dir

    os.chdir(tmp_path / "foo/root")
    config = Config.find_or_default()
    assert sorted([str(path) for path in config.entity_dirs]) == [
        str(tmp_path / "foo/root/.mun/entities"),
        str(tmp_path / "foo/sib1/.mun/entities"),
    ]


def test_custom_entity_dir_discovery(tmp_path, config_file):
    config_file(
        f"""entity_dir_patterns = [".entities", "../entities", "{tmp_path / "bar"}/ents"]"""
    )

    (tmp_path / "foo/root/.mun/entities").mkdir(parents=True)
    (tmp_path / "foo/sib1/.mun").mkdir(parents=True)
    (tmp_path / "foo/sib1/.entities").mkdir(parents=True)
    (tmp_path / "foo/sib2/.mun").mkdir(parents=True)
    (tmp_path / "foo/entities").mkdir(parents=True)
    (tmp_path / "bar/ents").mkdir(parents=True)

    os.chdir(tmp_path / "foo/root")
    config = Config.find_or_default()
    assert sorted([str(path) for path in config.entity_dirs]) == [
        str(tmp_path / "bar/ents"),
        str(tmp_path / "foo/entities"),
        str(tmp_path / "foo/sib1/.entities"),
    ]
