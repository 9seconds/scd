# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import subprocess


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

    if process.returncode != os.EX_OK:
        logging.warning(
            "Cannot execute %s (exit code %s): stdout=%s, stderr=%s",
            name, process.returncode, stdout, stderr)
        raise ValueError("Cannot execute {0}".format(name))

    return {
        "code": process.returncode,
        "stdout": stdout.decode("utf-8").strip().split("\n"),
        "stderr": stderr.decode("utf-8").strip().split("\n")}
