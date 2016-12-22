# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os.path
import shutil

import mock
import pytest

import scd.config
import scd.version


if hasattr(shutil, "which"):
    has_git = shutil.which("git")
else:
    import distutils.spawn
    has_git = distutils.spawn.find_executable("git")


@pytest.yield_fixture
def external_command():
    with mock.patch("scd.utils.execute") as mocked:
        yield mocked


@pytest.fixture
def git_dir():
    dirname = os.path.dirname(__file__)
    toplevel = os.path.dirname(dirname)
    return os.path.join(toplevel, ".git")


class VersionTest(object):

    SCHEME = "semver"

    def setup_method(self, method):
        config = {
            "version": {
                "scheme": self.SCHEME,
                "number": "1.2.3"
            },
            "files": []
        }
        self.config = scd.config.Config(pytest.faux.gen_alpha(), config)


class TestSemVer(VersionTest):

    SCHEME = "semver"

    @pytest.mark.parametrize("version", (
        "0", "0.", "0.1", "0.1.", "0.1.0rc1", "0.."
    ))
    def test_version_parse_nok(self, version):
        self.config.raw["version"]["number"] = version
        with pytest.raises(ValueError):
            self.config.version

    def test_version_parse_full(self):
        self.config.raw["version"]["number"] = "1.2.0-pre1+0"
        version = self.config.version

        assert version.version == "1.2.0-pre1+0"
        assert version.major == 1
        assert version.next_major == 2
        assert version.prev_major == 0
        assert version.minor == 2
        assert version.next_minor == 3
        assert version.prev_minor == 1
        assert version.patch == 0
        assert version.next_patch == 1
        assert version.prev_patch == 0
        assert version.prerelease == "pre1"
        assert version.next_prerelease == "pre2"
        assert version.prev_prerelease == "pre0"
        assert version.build == "0"
        assert version.next_build == "1"
        assert version.prev_build == "0"
        assert version.context == {
            "full": "1.2.0-pre1+0",
            "major": 1,
            "next_major": 2,
            "prev_major": 0,
            "minor": 2,
            "next_minor": 3,
            "prev_minor": 1,
            "patch": 0,
            "next_patch": 1,
            "prev_patch": 0,
            "prerelease": "pre1",
            "next_prerelease": "pre2",
            "prev_prerelease": "pre0",
            "build": "0",
            "next_build": "1",
            "prev_build": "0"
        }

    @pytest.mark.parametrize("pre", ("-1", ""))
    def test_parse_no_build(self, pre):
        self.config.raw["version"]["number"] = "1.2.0" + pre
        version = self.config.version

        assert version.build == ""
        assert version.next_build == ""
        assert version.prev_build == ""
        if pre == "-1":
            assert version.prerelease == "1"
        else:
            assert version.prerelease == ""

    @pytest.mark.parametrize("build", ("+1", ""))
    def test_parse_no_pre(self, build):
        self.config.raw["version"]["number"] = "1.2.0" + build
        version = self.config.version

        assert version.prerelease == ""
        assert version.next_prerelease == ""
        assert version.prev_prerelease == ""
        if build == "+1":
            assert version.build == "1"
        else:
            assert version.build == ""


@pytest.mark.usefixtures("external_command")
class TestGitSemver(VersionTest):

    SCHEME = "git_semver"


@pytest.mark.skipIf(has_git, reason="No git is found in PATH")
def test_git_tag_ok(git_dir):
    assert scd.version.git_tag(git_dir)


def test_git_tag_nok(git_dir, external_command):
    external_command.side_effect = ValueError
    assert scd.version.git_tag(git_dir) is None


@pytest.mark.skipIf(has_git, reason="No git is found in PATH")
def test_git_distance_ok(git_dir):
    assert scd.version.git_distance(git_dir)


@pytest.mark.skipIf(has_git, reason="No git is found in PATH")
def test_git_distance_no_tag(git_dir):
    assert scd.version.git_distance(git_dir, pytest.faux.gen_uuid()) is None
