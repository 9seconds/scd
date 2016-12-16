# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections
import logging

import six


Parser = collections.namedtuple("Parser", ["name", "func"])


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
            return parser.func(content)
        except Exception as exc:
            logging.warning("Cannot parse %s: %s", parser.name, exc)

    raise ValueError("Cannot parse {0}".format(fileobj.name))
