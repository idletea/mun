from __future__ import annotations

import os
from pathlib import PosixPath
import pytest
from mun.config import ENV_CONFIG_PATH, Config


def test_config_default():
    Config.find_or_default()


def test_config_from_default_file(make_config_file):
    make_config_file("""entity_dir_patterns = [".foo/entities"]""")
    assert Config.find_or_default().opts.entity_dir_patterns == [
        PosixPath(".foo/entities")
    ]


def test_config_from_env_var(fs, env):
    env(**{ENV_CONFIG_PATH: "/foo/bar.toml"})
    fs.create_file(
        "/foo/bar.toml",
        contents="""
    project_root_indicators = [".custom", ".git"]
    """,
    )

    assert Config.find_or_default().opts.project_root_indicators == [
        PosixPath(".custom"),
        PosixPath(".git"),
    ]


def test_default_project_root_discovery(fs):
    fs.create_file("/.mun")
    fs.create_file("/foo/.foo")
    fs.create_file("/foo/bar/.mun")
    fs.create_file("/foo/bar/baz/foo/.foo")

    for cd_to, expect_root in [
        ("/foo/bar/baz/foo", "/foo/bar"),
        ("/foo/bar", "/foo/bar"),
        ("/foo", "/"),
    ]:
        os.chdir(cd_to)
        actual_root = Config.find_or_default().project_root
        assert str(actual_root) == expect_root


def test_custom_project_root_discovery(fs, make_config_file):
    make_config_file("""project_root_indicators = [".foo", ".git"]""")
    fs.create_file("/foo/bar/.git")
    fs.create_file("/foo/bar/baz/.foo")
    fs.create_dir("/foo/bar/baz/foo/bar")

    for cd_to, expect_root in [
        ("/foo/bar/baz", "/foo/bar/baz"),
        ("/foo/bar", "/foo/bar"),
        ("/foo/bar/baz/foo/bar", "/foo/bar/baz"),
    ]:
        os.chdir(cd_to)
        actual_root = Config.find_or_default().project_root
        assert str(actual_root) == expect_root

    os.chdir("/foo")
    with pytest.raises(SystemExit):
        _ = Config.find_or_default().project_root


def test_project_root_is_root(fs):
    os.chdir("/")
    fs.create_file("/.mun")
    _ = Config.find_or_default().project_root


def test_default_sibling_root_discovery(fs):
    fs.create_dir("/foo/root/.mun")
    fs.create_dir("/foo/sib1/.mun")
    fs.create_dir("/foo/sib2/.mun")
    fs.create_dir("/foo/notsib/.not-mun")

    os.chdir("/foo/root")
    config = Config.find_or_default()
    assert sorted([str(path) for path in config.sibling_roots]) == [
        "/foo/sib1",
        "/foo/sib2",
    ]


def test_custom_sibling_root_discovery(fs, make_config_file):
    fs.create_dir("/proj/sib1/.mun")
    fs.create_dir("/proj/sib2/.mun")
    fs.create_dir("/proj/sib3/mun")
    fs.create_dir("/proj/notme")
    fs.create_dir("/foo/other/.mun")
    fs.create_dir("/foo/notme")
    fs.create_dir("/foo/root/.mun")

    os.chdir("/foo/root")
    make_config_file("""sibling_project_patterns = ["/proj/*", "../other"]""")
    assert sorted([str(path) for path in Config.find_or_default().sibling_roots]) == [
        "/foo/other",
        "/proj/sib1",
        "/proj/sib2",
    ]


def test_roots(fs):
    fs.create_dir("/foo/root/.mun")
    fs.create_dir("/foo/sib1/.mun")
    fs.create_dir("/foo/sib2/.mun")

    os.chdir("/foo/root")
    config = Config.find_or_default()
    assert sorted([str(path) for path in config.roots]) == [
        "/foo/root",
        "/foo/sib1",
        "/foo/sib2",
    ]


def test_default_entity_dir_discovery(fs):
    fs.create_dir("/foo/root/.mun/entities")
    fs.create_dir("/foo/sib1/.mun/entities")
    fs.create_dir("/foo/sib2/.mun/not-entities")

    fs.create_file("/foo/sib2/.mun/entities")

    os.chdir("/foo/root")
    config = Config.find_or_default()
    assert sorted([str(path) for path in config.entity_dirs]) == [
        "/foo/root/.mun/entities",
        "/foo/sib1/.mun/entities",
    ]


def test_custom_entity_dir_discovery(fs, make_config_file):
    make_config_file(
        """entity_dir_patterns = [".entities", "../entities", "/bar/ents"]"""
    )
    fs.create_dir("/foo/root/.mun/entities")
    fs.create_dir("/foo/sib1/.mun")
    fs.create_dir("/foo/sib1/.entities")
    fs.create_dir("/foo/sib2/.mun")
    fs.create_dir("/foo/entities")
    fs.create_dir("/bar/ents")

    os.chdir("/foo/root")
    config = Config.find_or_default()
    assert sorted([str(path) for path in config.entity_dirs]) == [
        "/bar/ents",
        "/foo/entities",
        "/foo/sib1/.entities",
    ]
