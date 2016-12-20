# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections
import json
import logging
import os.path

import jsonschema
import six

import scd.files
import scd.utils
import scd.version


Parser = collections.namedtuple("Parser", ["name", "func"])

CONFIG_SCHEMA = {
    "type": "object",
    "required": ["version", "files"],
    "properties": {
        "version": {
            "type": "object",
            "required": ["scheme", "number"],
            "properties": {
                "scheme": {
                    "type": "string",
                    "enum": sorted(scd.utils.get_version_plugins().keys())
                },
                "number": {
                    "oneOf": [
                        {"type": "number"},
                        {"type": "string"}
                    ]
                }
            }
        },
        "files": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string", "enum": ["default"]},
                    {
                        "type": "object",
                        "properties": {
                            "search": {"type": "string"},
                            "search_raw": {"type": "string"},
                            "replace": {"type": "string"},
                            "replace_raw": {"type": "string"}
                        }
                    }
                ]
            }
        },
        "search_patterns": {
            "type": "object",
            "additionalProperties": {"type": "string"}
        },
        "replacement_paterns": {
            "type": "object",
            "additionalProperties": {"type": "string"}
        },
        "defaults": {
            "type": "object",
            "additionalProperties": {"type": "string"}
        }
    }
}


@six.python_2_unicode_compatible
class Config(object):

    __slots__ = "raw", "configpath"

    @staticmethod
    def validate_schema(config):
        errors = []
        validator = jsonschema.Draft4Validator(
            CONFIG_SCHEMA, format_checker=jsonschema.FormatChecker())

        for err in validator.iter_errors(config):
            errors.append("{0}: {1}".format("/".join(err.path), err.message))

        return errors

    def __init__(self, configpath, config):
        errors = self.validate_schema(config)
        if errors:
            for error in errors:
                logging.error("Error in config: %s", error)
            logging.debug("Schema is \n%s",
                          json.dumps(CONFIG_SCHEMA, sort_keys=True, indent=4))
            raise ValueError("Incorrect config")

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
        return six.text_type(self.raw["version"]["number"])

    @property
    def files(self):
        return [scd.files.File(self, conf) for conf in self.raw["files"]]

    @property
    def replacement_patterns(self):
        return self.raw.get("replacement_patterns", {})

    @property
    def search_patterns(self):
        return self.raw.get("search_patterns", {})

    @property
    def defaults(self):
        return self.raw.get("defaults", {})

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
