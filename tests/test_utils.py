# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

import pytest

import scd.utils


def test_lru_cache():
    @scd.utils.lru_cache()
    def method(*args, **kwargs):
        return pytest.faux.gen_uuid()

    val1 = method()
    assert method() == method() == val1

    val2 = method("qq")
    assert method("qq") == method("qq") == val2

    val3 = method(qq=3)
    assert method(qq=3) == method(qq=3) == val3

    assert val1 != val2
    assert val2 != val3
    assert val1 != val3


def test_execute_ok():
    command = ["python", "-c",
               "import sys; sys.stdout.write('1'); sys.stderr.write('2')"]

    result = scd.utils.execute(command)
    assert result["code"] == os.EX_OK
    assert result["stdout"] == ["1"]
    assert result["stderr"] == ["2"]


def test_execute_nok():
    command = [
        "python", "-c",
        "import sys; sys.stdout.write('1'); sys.stderr.write('2'); sys.exit(3)"
    ]

    with pytest.raises(ValueError):
        scd.utils.execute(command)


def test_execute_unknown():
    with pytest.raises(ValueError):
        scd.utils.execute(["python28", "-c", ""])


def test_get_plugins_ok():
    plugins = scd.utils.get_plugins(scd.utils.VERSION_PLUGIN_NAMESPACE)

    assert "pep440" in plugins
    assert "git_pep440" in plugins
    assert "semver" in plugins
    assert "git_semver" in plugins


def test_get_plugins_nok():
    assert scd.utils.get_plugins("scd.xxx") == {}


def test_get_version_plugins():
    plugins = scd.utils.get_plugins(scd.utils.VERSION_PLUGIN_NAMESPACE)
    assert plugins == scd.utils.get_version_plugins()
