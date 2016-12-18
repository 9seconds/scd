# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging
import os
import os.path
import re

import packaging.version
import semver
import six

import scd.utils


def git_distance(git_dir, matcher="v*"):
    command = ["git", "--git-dir", git_dir,
               "describe", "--tags", "--match", matcher]
    try:
        result = scd.utils.execute(command)
    except ValueError:
        return None

    output = result["stdout"][0]
    try:
        distance = output.rsplit("-", 2)[1]
        return int(distance)
    except Exception as exc:
        logging.warning("Cannot parse git result %s: %s", distance, exc)
        return None


def git_tag(git_dir):
    command = ["git", "--git-dir", git_dir, "rev-parse", "--short", "HEAD"]

    try:
        result = scd.utils.execute(command)
    except ValueError:
        return None

    return result["stdout"][0]


@six.python_2_unicode_compatible
@six.add_metaclass(abc.ABCMeta)
class Version(object):

    def __init__(self, config):
        self.base_number = six.text_type(config.version_number)
        self._config = config

    def __str__(self):
        return "<{0.__class__.__name__}(base_number={0.base_number})>".format(
            self.base_number)

    @property
    @abc.abstractmethod
    def version(self):
        raise NotImplementedError()


@six.python_2_unicode_compatible
class Semver(Version):

    TEXT_VERSION_REGEXP = re.compile(r"\d+(?=\D*$)")

    @classmethod
    def parse_text_version(cls, version):
        if not version:
            return 0

        matcher = cls.TEXT_VERSION_REGEXP.search(version)
        return int(matcher.group(0)) if matcher is not None else 0

    @classmethod
    def next_text_version(cls, version):
        return 1 + cls.parse_text_version(version)

    @classmethod
    def prev_text_version(cls, version):
        return max(0, cls.parse_text_version(version) - 1)

    def __init__(self, config):
        super(Semver, self).__init__(config)

        self.parsed = semver.parse_version_info(self.base_number)

    def __getattr__(self, name):
        return getattr(self.parsed, name, "")

    def __str__(self):
        return (
            "<{0.__class__.__name__}("
            "major={0.major}, minor={0.minor}, patch={0.patch}, "
            "prerelease={0.prerelease!r}, build={0.build!r}"
            ")>").format(self)

    __repr__ = __str__

    @property
    def version(self):
        return self.base_number

    @property
    def next_major(self):
        return 1 + self.major

    @property
    def prev_major(self):
        return max(0, self.major - 1)

    @property
    def next_minor(self):
        return 1 + self.minor

    @property
    def prev_minor(self):
        return max(0, self.minor - 1)

    @property
    def next_patch(self):
        return 1 + self.patch

    @property
    def prev_patch(self):
        return max(0, self.patch - 1)

    @property
    def prerelease(self):
        return self.parsed.prerelease or ""

    @property
    def next_prerelease(self):
        return self.TEXT_VERSION_REGEXP.sub(
            lambda m: six.text_type(self.next_text_version(m.group(0))),
            self.prerelease)

    @property
    def prev_prerelease(self):
        return self.TEXT_VERSION_REGEXP.sub(
            lambda m: six.text_type(self.prev_text_version(m.group(0))),
            self.prerelease)

    @property
    def build(self):
        return self.parsed.build or ""

    @property
    def next_build(self):
        return re.sub(
            lambda m: six.text_type(self.next_text_version(m.group(0))),
            self.build)

    @property
    def prev_build(self):
        return self.TEXT_VERSION_REGEXP.sub(
            lambda m: six.text_type(self.prev_text_version(m.group(0))),
            self.build)


class GitSemVer(Semver):

    def __init__(self, config):
        super(GitSemVer, self).__init__(config)

        git_dir = os.path.join(self._config.project_directory, ".git")
        git_matcher = self._config.raw["version"].get("tag_glob", "v*")
        self.distance = git_distance(git_dir, git_matcher)
        self.tag = git_tag(git_dir)

    @property
    def prerelease(self):
        if self.distance is not None:
            return self.distance

        return super(GitSemVer, self).prerelease

    @property
    def build(self):
        return self.tag or ""

    @property
    def next_build(self):
        return ""

    @property
    def prev_build(self):
        return ""


@six.python_2_unicode_compatible
class PEP440(Version):

    def __init__(self, config):
        super(PEP440, self).__init__(config)

        self.parsed = packaging.version.parse(self.base_number)._version
        if isinstance(self.parsed, six.string_types):
            raise ValueError("Incorrect version {0}".format(self.base_number))

    @property
    def version(self):
        if self.epoch:
            consturcted = "{0}!".format(self.epoch)
        else:
            consturcted = ""

        consturcted += ".".join(six.text_type(p) for p in self.parsed.release)
        if self.prerelease:
            consturcted += "{0}{1}".format(
                self.prerelease_type, self.prerelease)
        if self.post:
            consturcted += ".post{0}".format(self.post)
        if self.dev:
            consturcted += ".dev{0}".format(self.dev)
        if self.local:
            consturcted += "+{0}".format(self.local)

        return consturcted

    def __str__(self):
        return (
            "<{0.__class__.__name__}("
            "major={0.major}, minor={0.minor}, patch={0.patch}, "
            "{0.prerelease_type}={0.prerelease}, post={0.post}, "
            "dev={0.dev}, local={0.local!r}"
            ")>").format(self)

    __repr__ = __str__

    @property
    def epoch(self):
        return self.parsed.epoch

    @property
    def major(self):
        try:
            return self.parsed.release[0]
        except IndexError:
            return 0

    @property
    def next_major(self):
        return 1 + self.major

    @property
    def prev_major(self):
        return max(0, self.major - 1)

    @property
    def minor(self):
        try:
            return self.parsed.release[1]
        except IndexError:
            return 0

    @property
    def next_minor(self):
        return 1 + self.minor

    @property
    def prev_minor(self):
        return max(0, self.minor - 1)

    @property
    def patch(self):
        try:
            return self.parsed.release[2]
        except IndexError:
            return 0

    @property
    def next_patch(self):
        return 1 + self.patch

    @property
    def prev_patch(self):
        return max(0, self.patch - 1)

    @property
    def prerelease(self):
        return self.parsed.pre[-1] if self.parsed.pre else 0

    @property
    def prerelease_type(self):
        return self.parsed.pre[0] if self.parsed.pre else ""

    @property
    def next_prerelease(self):
        return 1 + self.prerelease

    @property
    def prev_prerelease(self):
        return max(0, self.prerelease - 1)

    @property
    def dev(self):
        return self.parsed.dev[-1] if self.parsed.dev else 0

    @property
    def next_dev(self):
        return 1 + self.dev

    @property
    def prev_dev(self):
        return max(0, self.dev - 1)

    @property
    def post(self):
        return self.parsed.post[-1] if self.parsed.post else 0

    @property
    def next_post(self):
        return 1 + self.post

    @property
    def prev_post(self):
        return max(0, self.post - 1)

    @property
    def local(self):
        return ".".join(self.parsed.local or [])


class GitPEP440(PEP440):

    def __init__(self, config):
        super(GitPEP440, self).__init__(config)

        git_dir = os.path.join(self._config.project_directory, ".git")
        git_matcher = self._config.raw["version"].get("tag_glob", "v*")
        self.distance = git_distance(git_dir, git_matcher)
        self.tag = git_tag(git_dir)

    @property
    def dev(self):
        return self.distance or ""

    @property
    def prev_dev(self):
        return ""

    @property
    def next_dev(self):
        return ""

    @property
    def local(self):
        if self.tag:
            local = self.parsed.local or []
            local.insert(0, self.tag)
            return ".".join(local)

        return super(GitPEP440, self).local
