# -*- coding: utf-8 -*-
"""A set of various utils, used within scd."""


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
"""Entrypoint namespace for version plugins."""


if six.PY34:
    lru_cache = functools.lru_cache
else:
    def lru_cache(*args, **kwargs):
        """Implementation of LRU cache.

        This is a simple fallback implementation of such cache for
        Python 2.7, in 3.3 and later :py:func:`functools.lru_cache` is
        used instead.
        """
        cache = {}

        def outer_decorator(func):
            @six.wraps(func)
            def inner_decorator(*fargs, **fkwargs):
                key = "\x00".join(
                    six.text_type(hash(farg)) for farg in fargs)
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
    """Executor of external command and wrapper for result.

    This is a wrapper for :py:class:`subprocess.Popen` with stdin set to
    :file:`/dev/null`.

    It returns result like:

    .. code-block:: python

        {
            "code": 0,
            "stdout": ["this is a line of stdout", "and this is another"],
            "stderr": []
        }

    :param list[str] command: A command for :py:class:`subprocess.Popen` to
        execute.
    :return: Execution result.
    :rtype: dict
    :raises ValueError: if command is not possible to execute.
    """
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
    """A mapping of plugins (loaded) in given namespace.

    :param str namespace: The name of namespace to use.
    :return: Mapping for plugins (key is the name and value is loaded plugin).
    :rtype: dict
    """
    plugins = {}

    for plugin in pkg_resources.iter_entry_points(namespace):
        plugins[plugin.name] = plugin.load()

    return plugins


def get_version_plugins():
    """A mapping of scd version plugins."""
    return get_plugins(VERSION_PLUGIN_NAMESPACE)
