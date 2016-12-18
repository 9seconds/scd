# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections
import os.path
import re

import jinja2

import scd.utils


DEFAULT_REPLACEMENTS = {
    "major_minor_patch": "{{ major }}.{{ minor }}.{{ patch }}",
    "major_minor": "{{ major }}.{{ minor }}",
    "major": "{{ major }}",
}

SearchReplace = collections.namedtuple("SearchReplace", ["search", "replace"])


class File(object):

    def __init__(self, config, data):
        self.config = config
        self.data = data

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
            for k, v in self.config.raw["replacement_patterns"].items())

        return replacements

    @property
    def default_search_patterns(self):
        return {}

    @property
    def all_search_patterns(self):
        patterns = self.default_replacements.copy()
        patterns.update(
            (k, re.compile(v))
            for k, v in self.config.raw["search_patterns"].items())

        return patterns

    @property
    def default_search_pattern(self):
        return self.all_search_pattern[self.config.raw["defaults"]["search"]]

    @property
    def default_replace_pattern(self):
        return self.all_replacements[
            self.config.raw["defaults"]["replacement"]]

    @property
    def patterns(self):
        patterns = []

        for item in self.data["replacements"]:
            if "search_raw" in item:
                search_pattern = re.compile(item["search_raw"])
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
