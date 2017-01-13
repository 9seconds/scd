# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

import pytest

import scd.config


def test_ok(scheme, config, tmp_project):
    conf = scd.config.make_config(
        tmp_project.join("config.json").strpath, None, config, {"k": "v"})

    assert conf.configpath == tmp_project.join("config.json").strpath
    assert conf.project_directory == tmp_project.strpath
    assert conf.version_scheme == scheme
    assert conf.version_number == "1.2.3"
    assert conf.replacement_patterns == {
        "major2": "{{ major }}",
        "vreplace": "v{{ full }}"
    }
    assert conf.search_patterns == {
        "full_version_w_comment": "{{ %s }}(?=.*?\#\sFULL)" % scheme,
        "vsearch": "v{{ %s }}" % scheme,
        "full": "{{ %s }}" % scheme
    }
    assert conf.defaults == {
        "replacement": "major2",
        "search": scheme
    }
    assert conf.extra_context == {"k": "v"}

    filenames = {fileobj.filename for fileobj in conf.files}
    assert filenames == {
        "full_version", "major", "all", "complex",
        "vcomplex", "minor_major_patch", "minor_major", "clean"}
    assert len(conf.files) == len(filenames)

    assert conf.version.base_number == "1.2.3"


@pytest.mark.parametrize("errors", (
    {"scheme": "qqq"},
    {"number": {}},
    {"scheme": "qqq", "number": {}}
))
def test_invalid_schema(errors, config, tmp_project):
    config["version"].update(errors)

    assert len(errors) == len(scd.config.Config.validate_schema(config))
    with pytest.raises(ValueError):
        scd.config.V1Config(
            tmp_project.join("config.json").strpath, None, config, {})


@pytest.mark.parametrize("fileext", ("yaml", "json", "toml"))
def test_parsing_ok(fileext, config, tmp_project):
    with tmp_project.join("config." + fileext).open() as ffp:
        conf = scd.config.parse(ffp, None, {})
    assert conf.raw == config


def test_parsing_failed(tmp_project):
    with tmp_project.join("complex").open() as ffp, pytest.raises(ValueError):
        scd.config.parse(ffp, None, {})


def test_parsing_bytes(tmp_project, config):
    tmp_project.join("config.json").write(json.dumps(config).encode("utf-8"))
    with tmp_project.join("config.json").open() as ffp:
        conf = scd.config.parse(ffp, None, {})

    assert conf.raw == config
