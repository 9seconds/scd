# -*- coding: utf-8 -*-
"""All classes and routines related to files."""


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

try:
    from collections.abc import Hashable
except Exception as exc:
    from collections import Hashable


DEFAULT_REPLACEMENTS = {
    "base": "{{ base }}",
    "full": "{{ full }}"
}
"""A mapping of default replacements."""


@six.python_2_unicode_compatible
class SearchReplace(Hashable):
    """Class, which presents a pair of single search and replacement.

    :param regexp search: Search regular expression.
    :param replace: Replacement template
    :type replace: :py:class:`jinja2.Template`
    """

    __slots__ = "search", "replace"

    @staticmethod
    @scd.utils.lru_cache()
    def get_replacement(replace, version):
        """Return rendered template, taken context from version.

        :param replace: Template for replacement.
        :type replace: :py:class:`jinja2.Template`
        :param version: Version instance, where template takes context.
        :type version: :py:class:`scd.version.Version`
        :return: Rendered template, ready to insert.
        :rtype: str
        """
        return replace.render(**version.context)

    def __init__(self, search, replace):
        self.search = search
        self.replace = replace

    def __str__(self):
        return (
            "<{0.__class__.__name__}(search={0.search.pattern!r}, "
            "replace={0.replace!r})>").format(self)

    __repr__ = __str__

    def __hash__(self):
        return hash("|".join(
            [str(hash(self.search)), str(hash(self.replace))]))

    def process(self, version, text):
        """Process text according to given version.

        This does what is expected: search in text (as a rule, line from
        file) and inserts replacement where required.

        :param version: Version instance to use.
        :type version: :py:class:`scd.version.Version`
        :param str text: Text to process.
        :return: Processed line, after inserting replacement if needed.
            Return original line otherwise.
        :rtype: str
        """
        replacement = self.get_replacement(self.replace, version)
        modified_text = self.search.sub(replacement, text)

        if text != modified_text:
            logging.info("Modify %r to %r",
                         text.strip(), modified_text.strip())

        return modified_text


@six.python_2_unicode_compatible
class File(Hashable):
    """This is a wrapper for a file on FS which should be managed by scd.

    The same story as for :py:class:`scd.config.Config`: this wrapper is
    used for purposes of conveience mostly. Also, it is required when
    one need to emit a list of :py:class:`SearchReplace` instances for a
    file.

    :param str name: The name of the file from config (as is, not absolute
        one)
    :param config: Instance of used config.
    :type config: :py:class:`scd.config.Config`
    :param list data: A contents of search/replacement parts of the
        config.
    """

    __slots__ = "name", "config", "data"

    def __init__(self, name, data, config):
        self.name = name
        self.config = config
        self.data = data

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return (
            "<{0.__class__.__name__}(filename={0.filename!r}, "
            "path={0.path!r}, patterns={0.patterns})>").format(self)

    __repr__ = __str__

    @property
    def filename(self):
        r"""Relative filename of the file.

        The most cool part about this property is that such
        name is platform independent: on Windows it might be
        :file:`docs\conf.py`, on Linux: :file:`docs/conf.py`. That cool.

        :return: Native platform filename
        :rtype: str
        """
        return os.path.join(*self.name.split("/"))

    @property
    def path(self):
        """Absolute path to the file for current platform.

        :return: Native platform absolute path.
        :rtype: str
        """
        return os.path.join(self.config.project_directory, self.filename)

    @property
    def default_replacements(self):
        """Mapping of default replacements for a file.

        Key is the name of the replacement, value is an instance of
        :py:class:`jinja2.Template`.

        :return: Mapping of replacements.
        :rtype: dict[str, str]
        """
        return {k: make_template(v) for k, v in DEFAULT_REPLACEMENTS.items()}

    @property
    def all_replacements(self):
        """Mapping of all known replacements for a file.

        This mapping includes default replacements and those, defined
        in config file.

        Key is the name of the replacement, value is an instance of
        :py:class:`jinja2.Template`.

        :return: Mapping of replacements.
        :rtype: dict[str, str]
        """
        replacements = self.default_replacements.copy()
        replacements.update(
            (k, make_template(v))
            for k, v in self.config.replacement_patterns.items())

        return replacements

    @property
    def default_search_patterns(self):
        """Mapping of default search patterns for a file.

        Key is the name of the replacement, value is compiled regular
        expression.

        :return: Mapping of patterns.
        :rtype: dict[str, str]
        """
        return {
            name: make_pattern("{{ %s }}" % name, self.config)
            for name in scd.utils.get_version_plugins()
        }

    @property
    def all_search_patterns(self):
        """Mapping of all search patterns for a file.

        This mapping includes default patterns and those, defined
        in config file.

        Key is the name of the replacement, value is compiled regular
        expression.

        :return: Mapping of patterns.
        :rtype: dict[str, str]
        """
        patterns = self.default_search_patterns.copy()
        patterns.update(
            (k, make_pattern(v, self.config))
            for k, v in self.config.search_patterns.items())

        return patterns

    @property
    def default_search_pattern(self):
        """Property, returns default search pattern from config.

        :return: Default search pattern
        :rtype: Regular expression
        """
        return self.all_search_patterns[self.config.defaults["search"]]

    @property
    def default_replace_pattern(self):
        """Property, returns default replacement template from config.

        :return: Default replacement pattern
        :rtype: :py:class:`jinja2.Template`
        """
        return self.all_replacements[self.config.defaults["replacement"]]

    @property
    def patterns(self):
        """A list of search/replacements for a file, based on config.

        :return: List of instances for file management.
        :rtype: list[:py:class:`SearchReplace`]
        """
        patterns = []

        for item in self.data:
            if item == "default":
                patterns.append(SearchReplace(
                    self.default_search_pattern,
                    self.default_replace_pattern))
                continue

            if "search_raw" in item:
                search_pattern = make_pattern(item["search_raw"], self.config)
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
    """Function for creating template instance from text template.

    :param str template: Text template to process.
    :return: Correct template instance, based on given text.
    :rtype: :py:class:`jinja2.Template`
    """
    return jinja2.Template(template)


@scd.utils.lru_cache()
def make_pattern(base_pattern, config):
    """Function, which creates regular expression based on given pattern.

    Also, it injects all predefined search regexps like ``pep440`` etc.

    :param str base_pattern: Pattern to transform to regular expression
        instance.
    :return: Regular expression pattern
    :rtype: regexp
    :raises ValueError: if pattern cannot be parsed.
    """
    patterns = config.extra_context.copy()
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
    try:
        pattern = re.compile(pattern, re.VERBOSE | re.UNICODE)
    except Exception as exc:
        logging.error("Base pattern: %s, replaced %s, error: %s",
                      base_pattern, pattern, exc)
        raise ValueError("Cannot parse pattern {0}".format(base_pattern))

    return pattern


def validate_access(files):
    """Function, which validates access to the files.

    :param files: A list of files to check
    :type files: list[:py:class:`scd.files.File`]
    :return: Is all files are accessible or not
    :rtype: bool
    """
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
