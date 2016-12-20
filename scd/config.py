# -*- coding: utf-8 -*-
# TODO Config validation


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections
import logging
import os.path

import six

import scd.files
import scd.utils
import scd.version


Parser = collections.namedtuple("Parser", ["name", "func"])


@six.python_2_unicode_compatible
class Config(object):

    __slots__ = "raw", "configpath"

    def __init__(self, configpath, config):
        self.raw = config
        self.configpath = os.path.abspath(configpath)

    @property
    def project_directory(self):
        return os.path.dirname(self.configpath)

    @property
    def version_scheme(self):
        return self.raw["version"].get("scheme", "semver")

    @property
    @scd.utils.lru_cache()
    def version(self):
        plugins = scd.utils.get_version_plugins()
        return plugins[self.version_scheme](self)

    @property
    def version_number(self):
        return self.raw["version"]["number"]

    @property
    def files(self):
        return [scd.files.File(self, conf) for conf in self.raw["files"]]

    @property
    def replacement_patterns(self):
        return self.raw["replacement_patterns"]

    @property
    def search_patterns(self):
        return self.raw["search_patterns"]

    @property
    def defaults(self):
        return self.raw["defaults"]

    def __str__(self):
        return "<Config(path={0.configpath}, raw={0.raw})".format(self)

    __repr__ = __str__


def get_parsers():
    parsers = []

    try:
        import simplejson
    except ImportError:
        logging.debug("Use default json as JSON config parser.")
        import json
        parsers.append(Parser("JSON", json.loads))
    else:
        logging.debug("Use simplejson as JSON config parser.")
        parsers.append(Parser("JSON", simplejson.loads))

    try:
        import yaml
    except ImportError:
        logging.debug("PyYAML is not importable.")
        try:
            import ruamel.yaml
        except ImportError:
            logging.debug("ruamel.yaml is not importable.")
        else:
            logging.debug("Use ruamel.yaml for YAML config parser.")
            parsers.append(Parser("YAML", ruamel.yaml.safe_load))
    else:
        logging.debug("Use PyYAML for YAML config parser.")
        parsers.append(Parser("YAML", yaml.safe_load))

    try:
        import toml
    except ImportError:
        logging.debug("toml is not importable.")
    else:
        logging.debug("Use toml for TOML config parser.")
        parsers.append(Parser("TOML", toml.loads))

    return parsers


def parse(fileobj):
    content = fileobj.read()
    if not isinstance(content, six.string_types):
        content = content.decode("utf-8")

    for parser in get_parsers():
        try:
            parsed = parser.func(content)
            logging.info("Parsed config as %s", parser.name)
            break
        except Exception as exc:
            logging.warning("Cannot parse %s: %s", parser.name, exc)
    else:
        raise ValueError("Cannot parse {0}".format(fileobj.name))

    return Config(fileobj.name, parsed)
