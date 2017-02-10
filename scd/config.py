# -*- coding: utf-8 -*-
"""This module contains all routines, related to scd's configuration."""


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections
import json
import logging
import os.path
import re
import warnings

import jsonschema
import six

import scd.files
import scd.utils
import scd.version

try:
    from collections.abc import Hashable
except ImportError:
    from collections import Hashable


Parser = collections.namedtuple("Parser", ["name", "func"])
"""Just a named tuple, related to configuration parsers.

:param str name: human-readable name of the parser.
:param callable func: parser of the config, which should accept UTF-8 text of
    config as a first argument.
"""

V1_CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema",
    "type": "object",
    "required": ["version", "defaults", "files"],
    "properties": {
        "config": {
            "type": "number",
            "minimum": 1,
            "multipleOf": 1.0
        },
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
            "type": "object",
            "additionalProperties": {
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
                            },
                            "anyOf": [
                                {
                                    "required": ["search"],
                                    "not": {"required": ["search_raw"]}
                                },
                                {
                                    "required": ["search_raw"],
                                    "not": {"required": ["search"]}
                                },
                                {
                                    "required": ["replace"],
                                    "not": {"required": ["replace_raw"]}
                                },
                                {
                                    "required": ["replace_raw"],
                                    "not": {"required": ["replace"]}
                                }
                            ]
                        }
                    ]
                }
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
        "groups": {
            "type": "object",
            "additionalProperties": {"type": "string"}
        },
        "defaults": {
            "type": "object",
            "properties": {
                "search": {"type": "string"},
                "replacement": {"type": "string"}
            },
            "additionalProperties": False
        }
    }
}
"""`JSON Schema <http://json-schema.org/>`_ of parsed configuration (ver 1).

This valid by `Draft V4
<https://tools.ietf.org/html/draft-wright-json-schema-00>`_.
"""


@six.python_2_unicode_compatible
class Config(Hashable):
    """Wrapper over parsed configuration data.

    This wrapper provides methods for internal scd's implementation.

    You want to use this class to access configuration data.

    :param str configpath: Path to the configuration file (can be
        relative).
    :param str or None version_scheme: Explicit version scheme to use.
    :param dict config: Parsed configuration.
    :param dict[str, str] extra_context: Additional context to use
        in templates.
    :raises ValueError: if configuration is not valid to schema.
    """

    SCHEMA = {}
    """JSON schema to comply with."""

    @staticmethod
    def validate_schema(config):
        """Validate parsed content to comply with JSON Schema.

        :param dict config: Parsed configuration.
        :return: A list of errors, found during verification. If list is
            empty, everyting is valid.
        :rtype: list[str]
        """
        validator = jsonschema.Draft4Validator(
            V1_CONFIG_SCHEMA, format_checker=jsonschema.FormatChecker())

        return [
            "{0}: {1}".format("/".join(err.path), err.message)
            for err in validator.iter_errors(config)]

    def __hash__(self):
        return hash(self.configpath)

    def __init__(self, configpath, version_scheme, config, extra_context):
        errors = self.validate_schema(config)
        if errors:
            for error in errors:
                logging.error("Error in config: %s", error)
            logging.debug("Schema is \n%s",
                          json.dumps(self.SCHEMA, sort_keys=True, indent=4))
            raise ValueError("Incorrect config")

        self.raw = config
        self.configpath = os.path.abspath(configpath)
        self.extra_context = extra_context
        self.explicit_version_scheme = version_scheme

    def __str__(self):
        return (
            "<{0.__class__.__name__}(path={0.configpath}, "
            "raw={0.raw})".format(self))

    __repr__ = __str__

    @property
    def project_directory(self):
        """Absolute path to the directory with config file.

        :return: Absolute path to the directory.
        :rtype: str
        """
        return os.path.dirname(self.configpath)


class V1Config(Config):
    """Implementation of :py:class:`Config` for config version 1."""

    SCHEMA = V1_CONFIG_SCHEMA

    @property
    def version_scheme(self):
        """Scheme of the versioning from config file.

        For example, it can be ``git_pep440``.

        :return: Version scheme
        :rtype: str
        """
        if self.explicit_version_scheme:
            return self.explicit_version_scheme

        return self.raw["version"].get("scheme", "semver")

    @property
    @scd.utils.lru_cache()
    def version(self):
        """Instance of :py:class:`scd.version.Version`.

        This instance is created based on data from config file.

        :return: Version
        :rtype: :py:class:`scd.version.Version`
        """
        plugins = scd.utils.get_version_plugins()
        return plugins[self.version_scheme](self)

    @property
    def version_number(self):
        """Base version number from config file.

        :return: Literal number from config
        :rtype: str
        """
        return six.text_type(self.raw["version"]["number"])

    @property
    def files(self):
        """A list of files defines in config file.

        :return: List of file instances
        :rtype: list[:py:class:`scd.files.File`]
        """
        files = [
            scd.files.File(name, conf, self)
            for name, conf in self.raw["files"].items()
        ]
        return sorted(files, key=lambda item: item.path)

    @property
    def groups(self):
        """A list of groups defined in config file.

        :return: List of group names
        :rtype: list[str, str]
        """
        return self.raw.get("groups", {})

    @property
    def replacement_patterns(self):
        """A mapping of replacement patterns (name/repl) from config file.

        :return: Raw mapping, as is.
        :rtype: dict[str, str]
        """
        return self.raw.get("replacement_patterns", {})

    @property
    def search_patterns(self):
        """A mapping of search patterns (name/pattern) from config file.

        :return: Raw mapping, as is.
        :rtype: dict[str, str]
        """
        return self.raw.get("search_patterns", {})

    @property
    def defaults(self):
        """A mapping of default search/replace patterns from config file.

        :return: Raw mapping, as is.
        :rtype: dict[str, str]
        """
        return self.raw.get("defaults", {})

    def filter_files(self, required_groups, required_files):
        """Filter and return only those files which are required.

        This uses groups and ``required_files`` parameter filtering.

        :param list[str] required_groups: A list of mandatory groups
        :param list[str] required_files: A list of mandatory files
        :return: A list of files after filtering.
        :rtype: list[:py:class:`scd.files.File`]
        """
        required_files = {
            os.path.abspath(item.name) for item in required_files}
        if required_groups:
            required_groups = [
                os.path.join(self.project_directory, value + "$")
                for key, value in self.groups.items()
                if key in required_groups]

        def filterfunc(item):
            if required_groups:
                for glob in required_groups:
                    if re.match(glob, item.path):
                        break
                else:
                    return False
            if required_files:
                return item.path in required_files
            return True

        files = filter(filterfunc, self.files)
        files = list(files)

        return files


def get_parsers():
    """Function to detect locally available parsers.

    :return: A list of available parsers for config files.
    :rtype: list[:py:class:`Parser`]
    """
    parsers = [Parser("JSON", get_json_parser())]

    yaml_parser = get_yaml_parser()
    if yaml_parser:
        parsers.append(Parser("YAML", yaml_parser))

    toml_parser = get_toml_parser()
    if toml_parser:
        parsers.append(Parser("TOML", toml_parser))

    return parsers


def get_json_parser():
    """Function which detects what parser should be used for parsing JSONs.

    It uses following logic: if `simplejson
    <https://simplejson.readthedocs.io/en/latest/>`_ is available, it
    would be used, otherwise default :py:mod:`json` will work.

    :return: JSON parser
    :rtype: :py:class:`Parser`
    """
    try:
        import simplejson
    except ImportError:
        logging.debug("Use default json as JSON config parser.")
        import json
        return json.loads

    logging.debug("Use simplejson as JSON config parser.")
    return simplejson.loads


def get_yaml_parser():
    """Function which detects what parser should be used for parsing YAMLs.

    It uses following logic: if `PyYAML <http://pyyaml.org/>`_ is
    available, it would be used, otherwise it will try for `ruamel.yaml
    <https://bitbucket.org/ruamel/yaml>`_.

    :return: YAML parser or ``None`` if nothing found.
    :rtype: :py:class:`Parser` or None
    """
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
            return ruamel.yaml.safe_load
    else:
        logging.debug("Use PyYAML for YAML config parser.")
        return yaml.safe_load


def get_toml_parser():
    """Function which detects what parser should be used for parsing TOMLs.

    It uses following logic: if `toml <https://github.com/uiri/toml>`_ is
    available, it would be used, otherwise ``None`` is returned.

    :return: TOML parser or ``None`` if nothing found.
    :rtype: :py:class:`Parser` or None
    """
    try:
        import toml
    except ImportError:
        logging.debug("toml is not importable.")
    else:
        logging.debug("Use toml for TOML config parser.")
        return toml.loads


def parse(fileobj, version_scheme, extra_context):
    """Function which parses given file-like object with config data.

    :param fileobj: Open file object for parsing.
    :type fileobj: file-like object
    :param str or None version_scheme: Explicit version scheme to use.
    :param dict[str, str] extra_context: Additional context to use
        in templates.
    :return: Parsed config
    :rtype: :py:class:`Config`
    :raises ValueError: if not possible to parse config in any way.
    """
    content = fileobj.read()
    if not isinstance(content, six.string_types):
        content = content.decode("utf-8")

    for parser in get_parsers():
        try:
            parsed = parser.func(content)
            logging.info("Parsed config as %s", parser.name)
            logging.debug("Parsed config content:\n%s",
                          json.dumps(parsed, sort_keys=True, indent=4))
        except Exception as exc:
            logging.debug("Cannot parse %s: %s", parser.name, exc)
        else:
            return make_config(
                fileobj.name, version_scheme, parsed, extra_context)

    raise ValueError("Cannot parse {0}".format(fileobj.name))


def make_config(filename, version_scheme, content, extra_context):
    """Function to generate config based on incoming parameters.

    This function does validation of config version.

    :param str filename: Path to the configuration file (can be
        relative).
    :param str or None version_scheme: Explicit version scheme to use.
    :param dict content: Parsed configuration.
    :param dict[str, str] extra_context: Additional context to use
        in templates.
    :raises ValueError: if config version is not supported.
    """
    if not isinstance(content, dict):
        raise ValueError("Incorrect config format!")

    if "config" not in content:
        warnings.warn(
            "Please, set explicit version of config in your "
            "configuration file. It is not mandatory yet, but will "
            "in future. Implicit version is always 1, not latest.",
            FutureWarning
        )

    config_version = content.get("config", 1)
    if config_version == 1:
        return V1Config(filename, version_scheme, content, extra_context)

    raise ValueError("Unknown config version %s", config_version)
