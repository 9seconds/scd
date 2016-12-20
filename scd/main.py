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
import scd.files
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


def filter_files(all_files, required):
    if not required:
        return all_files

    required = {os.path.abspath(path.name) for path in required}
    return [fileobj for fileobj in all_files if fileobj.path in required]


@catch_exceptions
def main():
    global OPTIONS

    OPTIONS = get_options()
    configure_logging(OPTIONS)

    logging.debug("Options: %s", OPTIONS)

    config = scd.config.parse(OPTIONS.config)
    logging.debug("Version is %s", config.version)

    if not scd.files.validate_access(config.files):
        logging.error("Cannot process all files, so nothing to do.")

    for fileobj in filter_files(config.files, OPTIONS.files):
        logging.debug("Start to process %s", fileobj)
        process_file(fileobj, config)


def process_file(fileobj, config):
    need_to_save = False
    file_result = []

    with open(fileobj.path, "rt") as filefp:
        for line in filefp:
            original_line = line
            for sr in fileobj.patterns:
                line = sr.process(config.version, line)
                if original_line != line:
                    need_to_save = True
                    file_result.append(line)

    if not OPTIONS.dry_run and need_to_save:
        logging.info("Need to save %s", fileobj.path)
        with open(fileobj.path, "wt") as filefp:
            filefp.writelines(file_result)
    else:
        logging.info("No need to save %s", fileobj.path)


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
        "-c", "--config",
        metavar="CONFIG_PATH",
        type=argparse.FileType("rt"),
        default=".scd.yaml",
        help="Path to the config. Default is $(pwd)/.scd.yaml.")
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
