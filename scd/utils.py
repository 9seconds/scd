# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools
import logging
import os
import subprocess

import pkg_resources
import six


VERSION_PLUGIN_NAMESPACE = "scd.version"


if six.PY34:
    lru_cache = functools.lru_cache
else:
    def lru_cache(*args, **kwargs):
        cache = {}

        def outer_decorator(func):
            @six.wraps(func)
            def inner_decorator(*fargs, **fkwargs):
                key = "\x00".join(
                    six.text_type(hash(farg)) for farg in sorted(fargs))
                key += "\x00".join(
                    six.text_type(k) + "\x00" + six.text_type(hash(v))
                    for k, v in sorted(fkwargs.items()))
                if key in cache:
                    return cache[key]

                cache[key] = func(*fargs, **fkwargs)
                return cache[key]

            return inner_decorator
        return outer_decorator


def execute(command):
    name = command[0]

    try:
        with open(os.devnull, "w") as devnull:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=devnull)
            stdout, stderr = process.communicate()
    except OSError as exc:
        logging.warning("Cannot execute %s: %s", name, exc)
        raise ValueError("Cannot execute {0}".format(name))
    else:
        stdout = stdout.decode("utf-8").strip()
        stderr = stderr.decode("utf-8").strip()

    if process.returncode != os.EX_OK:
        logging.warning(
            "Cannot execute %s (exit code %s): stdout=%s, stderr=%s",
            name, process.returncode, stdout, stderr)
        raise ValueError("Cannot execute {0}".format(name))

    return {
        "code": process.returncode,
        "stdout": stdout.split("\n"),
        "stderr": stderr.split("\n")}


@lru_cache()
def get_plugins(namespace):
    plugins = {}

    for plugin in pkg_resources.iter_entry_points(namespace):
        plugins[plugin.name] = plugin.load()

    return plugins


def get_version_plugins():
    return get_plugins(VERSION_PLUGIN_NAMESPACE)
