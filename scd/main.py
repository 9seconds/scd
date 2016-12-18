# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import os.path
import sys

import six

import scd.config
import scd.version


DESCRIPTION = """
scd is a tool to manage version strings within your project files.
"""
"""Description of the tool."""

EPILOG = """
Please check GH of the SCD for issues and updates:
https://github.com/9seconds/scd
"""
"""Epilog for the argparser."""

OPTIONS = None
"""Commandline parameters."""


def catch_exceptions(func):
    @six.wraps(func)
    def decorator():
        try:
            func()
        except Exception as exc:
            if OPTIONS:
                if OPTIONS.debug:
                    logging.exception(exc)
                else:
                    print(exc, file=sys.stderr)
            return os.EX_SOFTWARE

        return os.EX_OK

    return decorator


@catch_exceptions
def main():
    global OPTIONS

    OPTIONS = get_options()
    configure_logging(OPTIONS)

    logging.debug("Options: %s", OPTIONS)

    config = scd.config.parse(OPTIONS.config)
    version = scd.version.GitPEP440(config)
    print(version.version)


def get_options():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG)

    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        default=False,
        help="run in debug mode")
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        default=False,
        help="make dry run, do not change anything.")

    parser.add_argument(
        "config",
        metavar="CONFIG_PATH",
        nargs=argparse.OPTIONAL,
        type=argparse.FileType("rt"),
        default=".scd.yaml",
        help="Path to the config.")
    parser.add_argument(
        "files",
        metavar="FILE_PATH",
        nargs=argparse.ZERO_OR_MORE,
        type=argparse.FileType("rt"),
        help=(
            "Path to the files where to make version bumping. "
            "If nothing is set, all filenames in config will be used."))

    return parser.parse_args()


def configure_logging(options):
    logging.basicConfig(
        level=(logging.DEBUG if options.debug else logging.ERROR),
        format="[%(levelname)-5s] (%(module)10s:%(lineno)-3d) %(message)s")


if __name__ == "__main__":
    sys.exit(main())
