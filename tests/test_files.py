# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

import pytest

import scd.files
import scd.utils


@pytest.mark.parametrize("replacement", ("base", "full"))
def test_default_replacements(replacement):
    assert replacement in scd.files.DEFAULT_REPLACEMENTS


@pytest.fixture
def minimal_config():
    config = {
        "version": {
            "scheme": "semver",
            "number": "1.2.3-pre1+build10"
        },
        "files": {}
    }
    return scd.config.Config(pytest.faux.gen_alpha(), config, {})


@pytest.fixture
def full_config(config, tmp_project):
    config_file = tmp_project.join("config.json").strpath
    return scd.config.Config(config_file, config, {"k": "v"})


@pytest.fixture
def firstfile(full_config):
    for fobj in full_config.files:
        if fobj.filename == "full_version":
            return fobj
    pytest.fail("Cannot find full_version fileobj")


class TestSearchReplace(object):

    def test_replace_nothing(self, minimal_config):
        search_pattern = scd.files.make_pattern(r"\W+", minimal_config)
        replacement = scd.files.make_template("{{ major }}")
        sr = scd.files.SearchReplace(search_pattern, replacement)

        assert "hello" == sr.process(minimal_config.version, "hello")

    @pytest.mark.parametrize("repl, result", (
        ("{{ base }}", "1.2.3-pre1+build10"),
        ("{{ full }}", "1.2.3-pre1+build10"),
        ("{{ major }}", "1"),
        ("{{ major }}.{{ minor }}", "1.2"),
        ("{{ major }}{% if minor %}.{{ minor }}{% endif %}", "1.2"),
        ("{{ major }}{% if minor %}.{{ minor }}{% endif %}.{{ patch }}",
         "1.2.3"),
        ("{{ major }}{% if minor %}.{{ minor }}{% endif %}{% if patch > 10 %}"
         ".{{ patch }}{% endif %}", "1.2"),
    ))
    def test_replace(self, minimal_config, repl, result):
        search_pattern = scd.files.make_pattern(r"\w+", minimal_config)
        replacement = scd.files.make_template(repl)
        sr = scd.files.SearchReplace(search_pattern, replacement)

        assert result == sr.process(minimal_config.version, "hello")


class TestFile(object):

    def test_filename(self, firstfile):
        assert firstfile.filename == "full_version"

    def test_assert_path(self, firstfile, tmp_project):
        assert firstfile.path == tmp_project.join("full_version").strpath

    def test_default_replacements(self, firstfile):
        assert firstfile.default_replacements == {
            k: scd.files.make_template(v)
            for k, v in scd.files.DEFAULT_REPLACEMENTS.items()}

    def test_all_replacements(self, firstfile):
        assert firstfile.all_replacements == {
            "base": scd.files.make_template(
                scd.files.DEFAULT_REPLACEMENTS["base"]),
            "full": scd.files.make_template(
                scd.files.DEFAULT_REPLACEMENTS["full"]),
            "major2": scd.files.make_template("{{ major }}"),
            "vreplace": scd.files.make_template("v{{ full }}")
        }

    def test_default_search_patterns(self, full_config, firstfile):
        assert firstfile.default_search_patterns == {
            name: scd.files.make_pattern("{{ %s }}" % name, full_config)
            for name in scd.utils.get_version_plugins()
        }

    def test_all_search_patterns(self, scheme, full_config, firstfile):
        assert firstfile.all_search_patterns == dict(list({
            "full": scd.files.make_pattern("{{ %s }}" % scheme, full_config),
            "full_version_w_comment": scd.files.make_pattern(
                "{{ %s }}(?=.*?\#\sFULL)" % scheme, full_config),
            "vsearch": scd.files.make_pattern("v{{ %s }}" % scheme,
                                              full_config)
        }.items()) + list(firstfile.default_search_patterns.items()))

    def test_default_search_pattern(self, scheme, full_config, firstfile):
        assert firstfile.default_search_pattern == scd.files.make_pattern(
            "{{ %s }}" % scheme, full_config)

    def test_default_replacement_pattern(self, firstfile):
        assert firstfile.default_replace_pattern == scd.files.make_template(
            "{{ major }}")

    def test_patterns(self, full_config):
        for fileobj in full_config.files:
            assert fileobj.patterns


def test_validate_access_ok(full_config):
    assert scd.files.validate_access(full_config.files)


def test_validate_access_absentfile(full_config, tmp_project):
    tmp_project.join("full_version").remove()
    assert not scd.files.validate_access(full_config.files)


def test_validate_access_not_a_file(full_config, tmp_project):
    tmp_project.join("full_version").remove()
    tmp_project.join("full_version").mkdir()
    assert not scd.files.validate_access(full_config.files)


@pytest.mark.parametrize("perm", (os.R_OK, os.W_OK))
def test_validate_access_not_accessible(perm, full_config, tmp_project):
    tmp_project.join("full_version").chmod(perm)
    assert not scd.files.validate_access(full_config.files)
