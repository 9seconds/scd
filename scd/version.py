# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re

import semver
import six


@six.python_2_unicode_compatible
class Version(object):

    def __init__(self, base_number):
        self.base_number = base_number

    def __str__(self):
        return "<{0.__class__.__name__}(base_number={0.base_number})>".format(
            self.base_number)


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

    def __init__(self, base_number):
        super(Semver, self).__init__(base_number)

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
        return re.sub(
            self.TEXT_VERSION_REGEXP,
            lambda m: six.text_type(self.next_text_version(m.group(0))),
            self.prerelease)

    @property
    def prev_prerelease(self):
        return re.sub(
            self.TEXT_VERSION_REGEXP,
            lambda m: six.text_type(self.prev_text_version(m.group(0))),
            self.prerelease)

    @property
    def build(self):
        return self.parsed.build or ""

    @property
    def next_build(self):
        return re.sub(
            self.TEXT_VERSION_REGEXP,
            lambda m: six.text_type(self.next_text_version(m.group(0))),
            self.build)

    @property
    def prev_build(self):
        return re.sub(
            self.TEXT_VERSION_REGEXP,
            lambda m: six.text_type(self.prev_text_version(m.group(0))),
            self.build)
