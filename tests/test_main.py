# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import os.path
import sys

import pytest

import scd.config
import scd.main


@pytest.fixture
def cliargs(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["scd"])


@pytest.fixture
def options(monkeypatch, cliargs):
    monkeypatch.setattr(scd.main, "OPTIONS", scd.main.get_options())


@pytest.yield_fixture
def chdir_to_current():
    current = os.path.dirname(__file__)
    old_dir = os.getcwd()
    yield os.chdir(current)
    os.chdir(old_dir)


@pytest.yield_fixture
def chdir_to_tmpproject(tmp_project):
    old_dir = os.getcwd()
    yield os.chdir(tmp_project.strpath)
    os.chdir(old_dir)


@pytest.fixture
def conf(config):
    return scd.config.Config(pytest.faux.gen_alpha(), config, {})


def test_catch_exception_ok(options):
    @scd.main.catch_exceptions
    def func():
        return 1

    assert func() == os.EX_OK


def test_catch_exception_nok(options):
    @scd.main.catch_exceptions
    def func():
        raise ValueError

    assert func() != os.EX_OK


def test_guess_configfile(options, chdir_to_current):
    configfile = os.path.dirname(__file__)
    configfile = os.path.dirname(configfile)
    configfile = os.path.join(configfile, ".scd.yaml")

    with scd.main.guess_configfile() as ffp:
        assert configfile == ffp.name


def test_main(chdir_to_tmpproject, conf, cliargs):
    sys.argv.extend(["-c", "config.json"])

    assert scd.main.main() == os.EX_OK

    with open("full_version") as ffp:
        assert ffp.read() == "1.2.3"
