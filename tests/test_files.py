# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import re

import pytest

import scd.files


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
        "files": []
    }
    return scd.config.Config(pytest.faux.gen_alpha(), config)


@pytest.fixture
def full_config(config, tmp_project):
    config_file = tmp_project.join("config.json").strpath
    return scd.config.Config(config_file, config)


class TestSearchReplace(object):

    def test_replace_nothing(self, minimal_config):
        search_pattern = scd.files.make_pattern(r"\W+")
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
        search_pattern = scd.files.make_pattern(r"\w+")
        replacement = scd.files.make_template(repl)
        sr = scd.files.SearchReplace(search_pattern, replacement)

        assert result == sr.process(minimal_config.version, "hello")


class TestFile(object):

    def test_filename(self, full_config):
        files = full_config.files
        assert full_config.files[0].filename == "c"
