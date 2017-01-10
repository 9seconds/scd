# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
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


@pytest.yield_fixture
def git_tag():
    with mock.patch.object(scd.version, "git_tag") as mocked:
        yield mocked


@pytest.yield_fixture
def git_distance():
    with mock.patch.object(scd.version, "git_distance") as mocked:
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
            "defaults": {"search": "semver", "replacement": "full"},
            "files": {}
        }
        self.config = scd.config.make_config(pytest.faux.gen_alpha(), config,
                                             {"k": "v"})


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

        assert version.full == "1.2.0-pre1+0"
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
            "base": "1.2.0-pre1+0",
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
            "prev_build": "0",
            "k": "v"
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

    def test_empty_version(self):
        assert scd.version.SemVer.parse_text_version("") == 0


@pytest.mark.usefixtures("external_command")
class TestGitSemver(VersionTest):

    SCHEME = "git_semver"

    @pytest.mark.parametrize("version", (
        "0", "0.", "0.1", "0.1.", "0.1.0rc1", "0.."
    ))
    def test_version_parse_nok(self, version):
        self.config.raw["version"]["number"] = version
        with pytest.raises(ValueError):
            self.config.version

    def test_version_parse_full(self, git_distance, git_tag):
        tag_name = pytest.faux.gen_alpha()
        tag_distance = str(abs(pytest.faux.gen_integer()))

        git_distance.return_value = tag_distance
        git_tag.return_value = tag_name

        self.config.raw["version"]["number"] = "1.2.0"
        version = self.config.version

        assert version.full == "1.2.0-{0}+{1}".format(tag_distance, tag_name)
        assert version.base == "1.2.0"
        assert version.major == 1
        assert version.next_major == 2
        assert version.prev_major == 0
        assert version.minor == 2
        assert version.next_minor == 3
        assert version.prev_minor == 1
        assert version.patch == 0
        assert version.next_patch == 1
        assert version.prev_patch == 0
        assert version.prerelease == tag_distance
        assert version.next_prerelease == str(
            scd.version.SemVer.next_text_version(tag_distance))
        assert version.prev_prerelease == str(
            scd.version.SemVer.prev_text_version(tag_distance))
        assert version.build == tag_name
        assert version.next_build == ""
        assert version.prev_build == ""
        assert version.context == {
            "full": "1.2.0-{0}+{1}".format(tag_distance, tag_name),
            "base": "1.2.0",
            "major": 1,
            "next_major": 2,
            "prev_major": 0,
            "minor": 2,
            "next_minor": 3,
            "prev_minor": 1,
            "patch": 0,
            "next_patch": 1,
            "prev_patch": 0,
            "prerelease": tag_distance,
            "next_prerelease": version.next_prerelease,
            "prev_prerelease": version.prev_prerelease,
            "build": tag_name,
            "next_build": "",
            "prev_build": "",
            "k": "v"
        }

    def test_empty_distance(self, git_dir, git_distance, git_tag):
        git_distance.return_value = None
        self.config.raw["version"]["number"] = "1.2.0"
        version = self.config.version

        assert version.prerelease == ""


class TestPEP440(VersionTest):

    SCHEME = "pep440"

    @pytest.mark.parametrize("version", ("0..", ""))
    def test_version_parse_nok(self, version):
        self.config.raw["version"]["number"] = version
        with pytest.raises(ValueError):
            self.config.version

    def test_version_parse_full(self):
        self.config.raw["version"]["number"] = \
            "12!1.2.0rc3.post3.dev0+local.dd"
        version = self.config.version

        assert version.base == "12!1.2.0rc3.post3.dev0+local.dd"
        assert version.full == "12!1.2.0rc3.post3+local.dd"
        assert version.maximum == "12!1.2.0rc3.post3.dev0+local.dd"
        assert version.epoch == 12
        assert version.major == 1
        assert version.next_major == 2
        assert version.prev_major == 0
        assert version.minor == 2
        assert version.next_minor == 3
        assert version.prev_minor == 1
        assert version.patch == 0
        assert version.next_patch == 1
        assert version.prev_patch == 0
        assert version.prerelease_type == "rc"
        assert version.prerelease == 3
        assert version.next_prerelease == 4
        assert version.prev_prerelease == 2
        assert version.dev == 0
        assert version.next_dev == 1
        assert version.prev_dev == 0
        assert version.post == 3
        assert version.next_post == 4
        assert version.prev_post == 2
        assert version.local == "local.dd"

        assert version.context == {
            "full": version.full,
            "base": version.base,
            "maximum": version.maximum,
            "major": version.major,
            "epoch": version.epoch,
            "next_major": version.next_major,
            "prev_major": version.prev_major,
            "minor": version.minor,
            "next_minor": version.next_minor,
            "prev_minor": version.prev_minor,
            "patch": version.patch,
            "next_patch": version.next_patch,
            "prev_patch": version.prev_patch,
            "prerelease_type": version.prerelease_type,
            "prerelease": version.prerelease,
            "next_prerelease": version.next_prerelease,
            "prev_prerelease": version.prev_prerelease,
            "dev": version.dev,
            "next_dev": version.next_dev,
            "prev_dev": version.prev_dev,
            "post": version.post,
            "prev_post": version.prev_post,
            "next_post": version.next_post,
            "local": version.local,
            "k": "v"
        }

    def test_no_epoch(self):
        self.config.raw["version"]["number"] = \
            "1.2.0rc3.post3.dev0+local.dd"
        assert self.config.version.epoch == 0


@pytest.mark.usefixtures("external_command")
class TestGitPEP440(VersionTest):

    SCHEME = "git_pep440"

    @pytest.mark.parametrize("version", ("0..", ""))
    def test_version_parse_nok(self, version):
        self.config.raw["version"]["number"] = version
        with pytest.raises(ValueError):
            self.config.version

    @pytest.mark.parametrize("distance", (0, 7))
    def test_dev(self, distance, git_tag, git_distance):
        git_distance.return_value = distance
        self.config.raw["version"]["number"] = "0.0.0"

        assert self.config.version.dev == distance

    @pytest.mark.parametrize("local", ("", "xxx"))
    def test_local(self, local, git_tag, git_distance):
        git_tag.return_value = local
        self.config.raw["version"]["number"] = "0.0.0+loc.dd"

        if local:
            assert self.config.version.local == "xxx.loc.dd"
        else:
            assert self.config.version.local == "loc.dd"


@pytest.mark.skipIf(has_git, reason="No git is found in PATH")
def test_git_tag_ok(git_dir):
    assert scd.version.git_tag(git_dir)


def test_git_tag_nok(git_dir, external_command):
    external_command.side_effect = ValueError
    assert scd.version.git_tag(git_dir) is None


@pytest.mark.skipIf(has_git, reason="No git is found in PATH")
def test_git_distance_ok(git_dir):
    scd.version.git_distance(git_dir)


@pytest.mark.skipIf(has_git, reason="No git is found in PATH")
def test_git_distance_no_tag(git_dir):
    assert scd.version.git_distance(git_dir, pytest.faux.gen_uuid()) is None


def test_git_distance_no_distance(git_dir, external_command):
    external_command.return_value = {
        "code": os.EX_OK,
        "stdout": ["v0.1.0"],
        "stderr": []
    }

    assert scd.version.git_distance(git_dir, pytest.faux.gen_uuid()) == 0
