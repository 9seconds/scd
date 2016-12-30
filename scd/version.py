# -*- coding: utf-8 -*-
"""Routines for version management.

These module has :py:class:`Version` class which is a base class for
entrypoints ``scd.version``. All entrypoints of such class should be
subclasses of :py:class:`Version`.

Currently, it ``scd.version`` has following defined entrypoints:

+------------+-----------------------+
| Entrypoint | Class                 |
+============+=======================+
| pep440     | :py:class:`PEP440`    |
+------------+-----------------------+
| semver     | :py:class:`SemVer`    |
+------------+-----------------------+
| git_pep440 | :py:class:`GitPEP440` |
+------------+-----------------------+
| git_semver | :py:class:`GitSemVer` |
+------------+-----------------------+
"""


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

try:
    from collections.abc import Hashable
except ImportError:
    from collections import Hashable


class GitMixin(Hashable):
    """Mixin to add Git flavor for :py:class:`Version` classes."""

    def __init__(self, *args, **kwargs):
        git_dir = os.path.join(self._config.project_directory, ".git")
        git_matcher = self._config.raw["version"].get("tag_glob", "v*")
        self.distance = git_distance(git_dir, git_matcher)
        if self.distance == 0:
            self.tag = ""
        else:
            self.tag = git_tag(git_dir)

    def __hash__(self):
        return hash("|".join([
            self.__class__.__name__,
            six.text_type(self.base_number),
            six.text_type(self.distance),
            six.text_type(self.tag)
        ]))


@six.python_2_unicode_compatible
@six.add_metaclass(abc.ABCMeta)
class Version(Hashable):
    """Base class for version scheme.

    This class is the base of ``scd.version`` entrypoint and it's
    main intention is correct version parsing and creating of
    template context.

    :param config: Configuration wrapper
    :type config: :py:class:`scd.config.Config`
    """

    REGEXP = re.compile(r"\d+\.\d+\.\d+")
    """Regular exprssion which is used for parsing base number.

    Each subclass has it's own regexp.
    """

    def __init__(self, config):
        self.base_number = six.text_type(config.version_number)
        self._config = config

    def __hash__(self):
        return hash("|".join([
            self.__class__.__name__,
            six.text_type(self.base_number)
        ]))

    def __str__(self):
        return "<{0.__class__.__name__}(base_number={0.base_number})>".format(
            self.base_number)

    @property
    def base(self):
        """Base number from config. Literally, as defined there.

        :return: Version number
        :rtype: str
        """
        return self.base_number

    @property
    @abc.abstractmethod
    def full(self):
        """Full reference version number, with a lot of details.

        :return: Version number
        :rtype: str
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def context(self):
        """Context for :py:class:`jinja2.Template`.

        :return: A mapping of context variables.
        :rtype: dict[str, str or int]
        """
        raise NotImplementedError()


@six.python_2_unicode_compatible
class SemVer(Version):
    """Implementation of semantic version numbering.

    For details, please check http://semver.org/.
    """

    TEXT_VERSION_REGEXP = re.compile(r"\d+(?=\D*$)")
    """Regular expression matched latest number in the string."""

    REGEXP = semver._REGEX.pattern.strip()
    REGEXP = REGEXP.lstrip("^").rstrip("$").strip()
    REGEXP = re.compile(REGEXP, re.VERBOSE)

    @classmethod
    def parse_text_version(cls, text):
        """Method which extracts latest number from the string.

        Empty string implies 0. No number also implies 0.

        :param str text: Line to search in.
        :return: Latest number
        :rtype: int
        """
        if not text:
            return 0

        matcher = cls.TEXT_VERSION_REGEXP.search(text)
        return int(matcher.group(0)) if matcher is not None else 0

    @classmethod
    def next_text_version(cls, text):
        """Method which returns next number from the string.

        From string ``build10s`` it returns 11.

        :param str text: Line to search in.
        :return: Next number
        :rtype: int
        """
        return 1 + cls.parse_text_version(text)

    @classmethod
    def prev_text_version(cls, version):
        """Method which returns previous number from the string.

        From string ``build10s`` it returns 9.

        :param str text: Line to search in.
        :return: Next number
        :rtype: int
        """
        return max(0, cls.parse_text_version(version) - 1)

    def __init__(self, config):
        super(SemVer, self).__init__(config)

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
    def context(self):
        return {
            "full": self.full,
            "base": self.base,
            "major": self.major,
            "next_major": self.next_major,
            "prev_major": self.prev_major,
            "minor": self.minor,
            "next_minor": self.next_minor,
            "prev_minor": self.prev_minor,
            "patch": self.patch,
            "next_patch": self.next_patch,
            "prev_patch": self.prev_patch,
            "prerelease": self.prerelease,
            "next_prerelease": self.next_prerelease,
            "prev_prerelease": self.prev_prerelease,
            "build": self.build,
            "next_build": self.next_build,
            "prev_build": self.prev_build}

    @property
    def full(self):
        number = "{0.major}.{0.minor}.{0.patch}".format(self)
        if self.prerelease:
            number += "-{0.prerelease}".format(self)
        if self.build:
            number += "+{0.build}".format(self)

        return number

    @property
    def next_major(self):
        """Next major version number.

        Next major number of version ``1.2.3`` is 2.

        :return: Next major version number.
        :rtype: int
        """
        return 1 + self.major

    @property
    def prev_major(self):
        """Prev major version number.

        Previous major number of version ``1.2.3`` is 0.

        :return: Previous major version number.
        :rtype: int
        """
        return max(0, self.major - 1)

    @property
    def next_minor(self):
        """Next minor version number.

        Next minor number of version ``1.2.3`` is 3.

        :return: Next minor version number.
        :rtype: int
        """
        return 1 + self.minor

    @property
    def prev_minor(self):
        """Prev minor version number.

        Previous minor number of version ``1.2.3`` is 1.

        :return: Previous minor version number.
        :rtype: int
        """
        return max(0, self.minor - 1)

    @property
    def next_patch(self):
        """Next patch version number.

        Next patch number of version ``1.2.3`` is 4.

        :return: Next patch version number.
        :rtype: int
        """
        return 1 + self.patch

    @property
    def prev_patch(self):
        """Prev patch version number.

        Previous patch number of version ``1.2.3`` is 4.

        :return: Previous patch version number.
        :rtype: int
        """
        return max(0, self.patch - 1)

    @property
    def prerelease(self):
        """Prerelase version number.

        Prerelase version number of version ``1.2.3-pre1+build4`` is pre1.

        :return: Prerelase version number.
        :rtype: str
        """
        return self.parsed.prerelease or ""

    @property
    def next_prerelease(self):
        """Next prerelase version number.

        Next prerelase version number of version ``1.2.3-pre1+build4``
        is pre2.

        :return: Next prerelase version number.
        :rtype: str
        """
        return self.TEXT_VERSION_REGEXP.sub(
            lambda m: six.text_type(self.next_text_version(m.group(0))),
            self.prerelease)

    @property
    def prev_prerelease(self):
        """Prev prerelase version number.

        Previous prerelase version number of version
        ``1.2.3-pre1+build4`` is pre0.

        :return: Previous prerelase version number.
        :rtype: str
        """
        return self.TEXT_VERSION_REGEXP.sub(
            lambda m: six.text_type(self.prev_text_version(m.group(0))),
            self.prerelease)

    @property
    def build(self):
        """Build version number.

        Build version number of version ``1.2.3-pre1+build4`` is build4.

        :return: Build version number.
        :rtype: str
        """
        return self.parsed.build or ""

    @property
    def next_build(self):
        """Next build version number.

        Next build version number of version ``1.2.3-pre1+build4`` is
        build5.

        :return: Next build version number.
        :rtype: str
        """
        return self.TEXT_VERSION_REGEXP.sub(
            lambda m: six.text_type(self.next_text_version(m.group(0))),
            self.build)

    @property
    def prev_build(self):
        """Prev build version number.

        Previous build version number of version ``1.2.3-pre1+build4``
        is build3.

        :return: Previous build version number.
        :rtype: str
        """
        return self.TEXT_VERSION_REGEXP.sub(
            lambda m: six.text_type(self.prev_text_version(m.group(0))),
            self.build)


class GitSemVer(GitMixin, SemVer):
    """Git flavored :py:class:`SemVer` implementation.

    This implementation does the same, but precalculates build and
    prerelase parts based on Git information.

    Prerelase is the number of commits since latest tag and build is
    short commit hash. Previous and next builds are always empty.
    Because nobody predicts next commit hash.
    """

    def __init__(self, config):
        SemVer.__init__(self, config)
        GitMixin.__init__(self, config)

    @property
    def prerelease(self):
        if self.distance is not None:
            return self.distance

        return ""

    @property
    def build(self):
        return self.tag or ""

    @property
    def next_build(self):
        return ""

    prev_build = next_build


@six.python_2_unicode_compatible
class PEP440(Version):
    """Implementation of Python versioning.

    For details, please check :pep:`440`.
    """

    REGEXP = packaging.version.VERSION_PATTERN.strip()
    REGEXP = re.compile(REGEXP, re.VERBOSE | re.IGNORECASE)

    def __init__(self, config):
        super(PEP440, self).__init__(config)

        self.parsed = packaging.version.parse(self.base_number)._version
        if isinstance(self.parsed, six.string_types):
            raise ValueError("Incorrect version {0}".format(self.base_number))

    @property
    def context(self):
        return {
            "full": self.full,
            "base": self.base,
            "epoch": self.epoch,
            "major": self.major,
            "maximum": self.maximum,
            "next_major": self.next_major,
            "prev_major": self.prev_major,
            "minor": self.minor,
            "next_minor": self.next_minor,
            "prev_minor": self.prev_minor,
            "patch": self.patch,
            "next_patch": self.next_patch,
            "prev_patch": self.prev_patch,
            "prerelease": self.prerelease,
            "prerelease_type": self.prerelease_type,
            "next_prerelease": self.next_prerelease,
            "prev_prerelease": self.prev_prerelease,
            "dev": self.dev,
            "local": self.local,
            "next_dev": self.next_dev,
            "prev_dev": self.prev_dev,
            "post": self.post,
            "next_post": self.next_post,
            "prev_post": self.prev_post}

    @property
    def full(self):
        if self.epoch:
            consturcted = "{0.epoch}!".format(self)
        else:
            consturcted = ""

        consturcted += ".".join(six.text_type(p) for p in self.parsed.release)
        if self.prerelease:
            consturcted += "{0.prerelease_type}{0.prerelease}".format(self)
        if self.post:
            consturcted += ".post{0.post}".format(self)
        if self.dev:
            consturcted += ".dev{0.dev}".format(self)
        if self.local:
            consturcted += "+{0.local}".format(self)

        return consturcted

    @property
    def maximum(self):
        """Maximal representation of the version.

        This always has all possible parts (probably except of
        prerelase, it is still optional, because we have to know
        context to calculate that) even if it makes no sense. I have no
        idea about usecase of that except of having this property for
        completenes.

        Example: ``0!1.2.3rc3.post0.dev0+1ubuntu1``.

        Horrible.

        :return: Maximal version number.
        :rtype: str
        """
        constructed = "{0.epoch}!{0.major}.{0.minor}.{0.patch}".format(self)
        if self.prerelease:
            constructed += "{0.prerelease_type}{0.prerelease}".format(self)
        constructed += ".post{0.post}.dev{0.dev}".format(self)
        if self.local:
            constructed += "+{0.local}".format(self)

        return constructed

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
        """Epoch part of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 1483072998.

        :return: Epoch part of the version number
        :rtype: int
        """
        return self.parsed.epoch

    @property
    def major(self):
        """Major part of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 1.

        :return: Major part of the version number
        :rtype: int
        """
        try:
            return self.parsed.release[0]
        except IndexError:
            return 0

    @property
    def next_major(self):
        """Next major number for the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 2.

        :return: Next major part of the version number
        :rtype: int
        """
        return 1 + self.major

    @property
    def prev_major(self):
        """Prev major number for the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 0.

        :return: Previous major part of the version number
        :rtype: int
        """
        return max(0, self.major - 1)

    @property
    def minor(self):
        """Minor number for the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 2.

        :return: Minor part of the version number
        :rtype: int
        """
        try:
            return self.parsed.release[1]
        except IndexError:
            return 0

    @property
    def next_minor(self):
        """Next minor number for the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 3.

        :return: Next minor part of the version number
        :rtype: int
        """
        return 1 + self.minor

    @property
    def prev_minor(self):
        """Prev minor number for the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 1.

        :return: Previous minor part of the version number
        :rtype: int
        """
        return max(0, self.minor - 1)

    @property
    def patch(self):
        """Patch number for the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 3.

        :return: Patch part of the version number
        :rtype: int
        """
        try:
            return self.parsed.release[2]
        except IndexError:
            return 0

    @property
    def next_patch(self):
        """Next patch number for the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 4.

        :return: Next patch part of the version number
        :rtype: int
        """
        return 1 + self.patch

    @property
    def prev_patch(self):
        """Prev patch number for the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 2.

        :return: Previous patch part of the version number
        :rtype: int
        """
        return max(0, self.patch - 1)

    @property
    def prerelease_type(self):
        """Type of the prerelase.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns rc.

        :return: Type of the prerelease
        :rtype: str
        """
        return self.parsed.pre[0] if self.parsed.pre else ""

    @property
    def prerelease(self):
        """Prerelease number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 3.

        :return: Prerelease part of the version number
        :rtype: int
        """
        return self.parsed.pre[-1] if self.parsed.pre else 0

    @property
    def next_prerelease(self):
        """Next prerelease number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 4.

        :return: Next prerelease part of the version number
        :rtype: int
        """
        return 1 + self.prerelease

    @property
    def prev_prerelease(self):
        """Prev prerelease number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 2.

        :return: Previous prerelease part of the version number
        :rtype: int
        """
        return max(0, self.prerelease - 1)

    @property
    def dev(self):
        """Dev number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 2.

        :return: Development part of the version number
        :rtype: int
        """
        return self.parsed.dev[-1] if self.parsed.dev else 0

    @property
    def next_dev(self):
        """Next dev number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 3.

        :return: Next development part of the version number
        :rtype: int
        """
        return 1 + self.dev

    @property
    def prev_dev(self):
        """Prev dev number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 2.

        :return: Previous development part of the version number
        :rtype: int
        """
        return max(0, self.dev - 1)

    @property
    def post(self):
        """Post number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 13.

        :return: Post part of the version number
        :rtype: int
        """
        return self.parsed.post[-1] if self.parsed.post else 0

    @property
    def next_post(self):
        """Next post number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 14.

        :return: Next post part of the version number
        :rtype: int
        """
        return 1 + self.post

    @property
    def prev_post(self):
        """Prev post number of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 12.

        :return: Previous post part of the version number
        :rtype: int
        """
        return max(0, self.post - 1)

    @property
    def local(self):
        """Local part of the version.

        For version ``1483072998!1.2.3rc3.post13.dev2+5afe90c.linux`` it
        returns 5afe90c.linux.

        :return: Local part of the version number
        :rtype: int
        """
        return ".".join(self.parsed.local or [])


class GitPEP440(GitMixin, PEP440):
    """Git flavored :py:class:`PEP440` implementation.

    This implementation does the same, but precalculates local and dev
    parts based on Git information.

    Dev release is the number of commits since latest tag and local will
    have Git short commit SHA at the first place.
    """

    def __init__(self, config):
        PEP440.__init__(self, config)
        GitMixin.__init__(self, config)

    @property
    def dev(self):
        return self.distance or 0

    @property
    def local(self):
        if self.tag:
            local = list(self.parsed.local or [])
            local.insert(0, self.tag)
            return ".".join(local)

        return super(GitPEP440, self).local


def git_distance(git_dir, matcher="v*"):
    """Return a number of commits since latest matched tag.

    :param str git_dir: Path to the :file:`.git` directory of
        repository.
    :param str matcher: Glob of the tag names to operate with.
    :return: The number of commits or ``None`` if nothing is found.
    :rtype: int or None
    """
    command = ["git", "--git-dir", git_dir,
               "describe", "--tags", "--match", matcher]
    try:
        result = scd.utils.execute(command)
    except ValueError:
        return None

    output = result["stdout"][0]
    try:
        distance = output.rsplit("-", 2)
        if len(distance) == 1:
            return 0
        return int(distance[1])
    except Exception as exc:
        logging.debug("Cannot parse git result %s: %s", distance, exc)
        return None


def git_tag(git_dir):
    """Return a current Git commit sha for repository.

    :param str git_dir: Path to the :file:`.git` directory of
        repository.
    :return: Commit SHA in short form or ``None`` if cannot find any.
    :rtype: str or None
    """
    command = ["git", "--git-dir", git_dir, "rev-parse", "--short", "HEAD"]

    try:
        result = scd.utils.execute(command)
    except ValueError:
        return None

    return result["stdout"][0]
