# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

import pytest
import toml
import yaml


@pytest.fixture(params=["git_pep440", "git_semver", "pep440", "semver"])
def scheme(request):
    return request.param


@pytest.fixture
def tmp_project(scheme, tmpdir):
    if scheme in ("pep440", "git_pep440"):
        tmpdir.join("full_version").write("0.1.0.post3.dev0+aab13f")
        tmpdir.join("all").write(
            """somecontent
            version="0.1.0.post3.dev0+aab13f"  # FULL

            some other content 0.1.0  # MAJOR_MINOR_PATCH
            lala 0.1 blabla  # MAJOR_MINOR
            qqq  0 sdfsdfsdf  # MAJOR
            """)
        tmpdir.join("complex").write("0.1.0.dev3")
    else:
        tmpdir.join("full_version").write("0.1.0-pre12+build11")
        tmpdir.join("all").write(
            """somecontent
            version="0.1.0-pre12+build11"  # FULL

            some other content 0.1.0  # MAJOR_MINOR_PATCH
            lala 0.1 blabla  # MAJOR_MINOR
            qqq  0 sdfsdfsdf  # MAJOR
            """)
        tmpdir.join("complex").write("0.1.0-2")

    tmpdir.join("vcomplex").write("v0.1.0")
    tmpdir.join("minor_major_patch").write("0.1.0")
    tmpdir.join("minor_major").write("HELLO 0.1 BYE")
    tmpdir.join("clean").write("nothing to do here")
    tmpdir.join("major").write("1")

    return tmpdir


@pytest.fixture
def config(scheme, tmp_project, tmpdir):
    new_config = {
        "version": {
            "scheme": scheme,
            "number": "1.2.3"
        },
        "files": {
            "full_version": [
                {
                    "search": "full",
                    "replace_raw": "{{ full }}"
                }
            ],
            "all": [
                {
                    "search": "full_version_w_comment",
                    "replace_raw": "{{ major }}.{{ patch }}.{{ minor }}"
                },
                {
                    "search_raw": "{{ major }}\.{{ minor }}\.{{ patch }}"
                    "(?=\s{2}\#\sMAJOR_MINOR_PATCH)",
                    "replace": "major2"
                },
                {"search_raw": "{{ major }}(?=.*?\#\sMAJOR)"}
            ],
            "vcomplex": [
                {"search": "vsearch", "replace": "vreplace"}
            ],
            "minor_major_patch": [
                {
                    "search": scheme,
                    "replace_raw": "{{ minor }}.{{ major }}.{{ patch }}"
                }
            ],
            "minor_major": [
                {
                    "search": scheme,
                    "replace_raw": "{{ major }}.{{ minor }}"
                }
            ],
            "major": ["default"],
            "clean": ["default"],
            "complex": ["default"]
        },
        "search_patterns": {
            "full": "{{ %s }}" % scheme,
            "full_version_w_comment": "{{ %s }}(?=.*?\#\sFULL)" % scheme,
            "vsearch": "v{{ %s }}" % scheme
        },
        "replacement_patterns": {
            "major2": "{{ major }}",
            "vreplace": "v{{ full }}"
        },
        "defaults": {
            "replacement": "major2",
            "search": scheme
        }
    }

    tmpdir.join("config.json").write(json.dumps(new_config))
    tmpdir.join("config.yaml").write(yaml.safe_dump(new_config))
    tmpdir.join("config.toml").write(toml.dumps(new_config))

    return new_config
