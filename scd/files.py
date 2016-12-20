# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import os.path
import re

import jinja2
import six

import scd.utils


DEFAULT_REPLACEMENTS = {
    "major_minor_patch": "{{ major }}.{{ minor }}.{{ patch }}",
    "major_minor": "{{ major }}.{{ minor }}",
    "major": "{{ major }}"}


@six.python_2_unicode_compatible
class SearchReplace(object):

    __slots__ = "search", "replace"

    def __init__(self, search, replace):
        self.search = search
        self.replace = replace

    def __str__(self):
        return (
            "<{0.__class__.__name__}(search={0.search.pattern!r}, "
            "replace={0.replace!r})>").format(self)

    def process(self, version, text, dry_run=False):
        replacement = self.replace.render(**version.context)
        modified_text = self.search.sub(replacement, text)

        if not dry_run:
            return modified_text
        if text != modified_text:
            logging.debug("Modify %r to %r", text, modified_text)

        return text

    __repr__ = __str__


@six.python_2_unicode_compatible
class File(object):

    __slots__ = "config", "data"

    def __init__(self, config, data):
        self.config = config
        self.data = data

    def __str__(self):
        return (
            "<{0.__class__.__name__}(filename={0.filename!r}, "
            "path={0.path!r}, patterns={0.patterns})>").format(self)

    __repr__ = __str__

    @property
    def filename(self):
        return self.data["filename"]

    @property
    def path(self):
        return os.path.join(self.config.project_directory, self.filename)

    @property
    def default_replacements(self):
        return {k: make_template(v) for k, v in DEFAULT_REPLACEMENTS.items()}

    @property
    def all_replacements(self):
        replacements = self.default_replacements.copy()
        replacements.update(
            (k, make_template(v))
            for k, v in self.config.replacement_patterns.items())

        return replacements

    @property
    def default_search_patterns(self):
        return {}

    @property
    def all_search_patterns(self):
        patterns = self.default_replacements.copy()
        patterns.update(
            (k, make_pattern(v))
            for k, v in self.config.search_patterns.items())

        return patterns

    @property
    def default_search_pattern(self):
        return self.all_search_patterns[self.config.defaults["search"]]

    @property
    def default_replace_pattern(self):
        return self.all_replacements[self.config.defaults["replacement"]]

    @property
    def patterns(self):
        patterns = []

        for item in self.data["replacements"]:
            if item == "default":
                patterns.append(SearchReplace(
                    self.default_search_pattern,
                    self.default_replace_pattern))
                continue

            if "search_raw" in item:
                search_pattern = make_pattern(item["search_raw"])
            elif "search" in item:
                search_pattern = self.all_search_patterns[item["search"]]
            else:
                search_pattern = self.default_search_pattern

            if "replace_raw" in item:
                replacement_pattern = make_template(item["replace_raw"])
            elif "replace" in item:
                replacement_pattern = self.all_replacements[item["replace"]]
            else:
                replacement_pattern = self.default_replace_pattern

            patterns.append(SearchReplace(search_pattern, replacement_pattern))

        return patterns


@scd.utils.lru_cache()
def make_template(template):
    return jinja2.Template(template)


@scd.utils.lru_cache()
def make_pattern(base_pattern):
    patterns = {}
    for name, data in scd.utils.get_version_plugins().items():
        if not hasattr(data, "REGEXP"):
            logging.warning("Plugin %s has no regexp, skip.")
            continue
        if not hasattr(data.REGEXP, "pattern"):
            logging.warning("Plugin %s regexp is not a pattern, skip.")
            continue
        patterns[name] = data.REGEXP.pattern

    pattern = make_template(base_pattern)
    pattern = pattern.render(**patterns)
    pattern = re.compile(pattern, re.VERBOSE)

    return pattern


def validate_access(files):
    ok = True

    for fileobj in files:
        if not os.path.isfile(fileobj.path):
            logging.error("Path %s is not a file.", fileobj.path)
            ok = False
        elif not os.access(fileobj.path, os.R_OK | os.W_OK):
            logging.error("File %s is not readable and writable.",
                          fileobj.path)
            ok = False
        else:
            logging.debug("File %s is ok", fileobj.path)

    return ok
