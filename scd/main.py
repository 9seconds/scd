# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import logging
import os
import os.path
import sys

import six

import scd.config
import scd.files
import scd.utils
import scd.version

try:
    import colorama
except ImportError:
    colorama = None


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
                elif OPTIONS.verbose:
                    logging.error(exc)
                else:
                    print(colorama.Fore.RED + six.text_type(exc),
                          file=sys.stderr)
            return os.EX_SOFTWARE

        return os.EX_OK

    return decorator


@catch_exceptions
def main():
    global OPTIONS

    OPTIONS = get_options()
    configure_logging()
    logging.debug("Options: %s", OPTIONS)

    config = scd.config.parse(guess_configfile())
    logging.info("Version is %s", config.version.version)

    for fobj in OPTIONS.files:
        fobj.close()

    if not scd.files.validate_access(config.files):
        logging.error("Cannot process all files, so nothing to do.")

    for fileobj in filter_files(config.files, OPTIONS.files):
        logging.info("Start to process %s", fileobj.path)
        logging.debug("Start to process %s", fileobj)
        process_file(fileobj, config)


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
        "-v", "--verbose",
        action="store_true",
        help="run tool in verbose mode")
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        default=False,
        help="make dry run, do not change anything.")
    parser.add_argument(
        "-c", "--config",
        metavar="CONFIG_PATH",
        default=None,
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


def filter_files(all_files, required):
    if not required:
        return all_files

    required = {os.path.abspath(path.name) for path in required}
    return [fileobj for fileobj in all_files if fileobj.path in required]


def process_file(fileobj, config):
    need_to_save = False
    file_result = []

    with codecs.open(fileobj.path, "rt", "utf-8") as filefp:
        for line in filefp:
            original_line = line
            for sr in fileobj.patterns:
                line = sr.process(config.version, line)
                if original_line != line:
                    need_to_save = True
                file_result.append(line)

    if not OPTIONS.dry_run and need_to_save:
        logging.debug("Need to save %s", fileobj.path)
        with codecs.open(fileobj.path, "wt", "utf-8") as filefp:
            filefp.writelines(file_result)
    else:
        logging.debug("No need to save %s", fileobj.path)


def guess_configfile():
    if OPTIONS.config:
        return codecs.open(OPTIONS.config, "rt")

    config = search_config_in_directory(os.getcwd())
    if not config:
        result = scd.utils.execute(["git", "rev-parse", "--show-toplevel"])
        if result["code"] == os.EX_OK:
            config = search_config_in_directory(result["stdout"][0])

    if not config:
        raise ValueError("Cannot find configfile.")

    return codecs.open(config, "rt")


def search_config_in_directory(directory):
    logging.debug("Search configfile in %s", directory)

    names = [".scd.json", "scd.json", ".scd.yaml", "scd.yaml", ".scd.toml",
             "scd.toml"]
    filenames = set(os.listdir(directory))
    for name in names:
        if name in filenames:
            name = os.path.join(directory, name)
            logging.info("Use %s as config file", name)
            return name

    logging.debug("No suitable configfile in %s", directory)


if colorama:
    def configure_logging():
        if OPTIONS.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format=(
                    colorama.Style.DIM
                    + "%(relativeCreated)d "
                    + colorama.Style.RESET_ALL + "["
                    + colorama.Fore.RED + "%(levelname)-7s"
                    + colorama.Style.RESET_ALL + "] ("
                    + colorama.Fore.GREEN + "%(module)10s"
                    + colorama.Style.RESET_ALL + ":"
                    + colorama.Fore.BLUE + "%(lineno)-3d"
                    + colorama.Style.RESET_ALL + ") %(message)s"
                )
            )
        elif OPTIONS.verbose:
            logging.basicConfig(
                level=logging.INFO,
                format=(
                    colorama.Style.DIM
                    + ">>> "
                    + colorama.Style.RESET_ALL
                    + "%(message)s"
                )
            )
        else:
            logging.basicConfig(level=logging.ERROR, format="%(message)s")
else:
    def configure_logging():
        if OPTIONS.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format=(
                    "%(relativeCreated)d [%(levelname)-7s] (%(module)10s"
                    ":%(lineno)-3d) %(message)s"
                )
            )
        elif OPTIONS.verbose:
            logging.basicConfig(level=logging.INFO, format=">>> %(message)s")
        else:
            logging.basicConfig(level=logging.ERROR, format="%(message)s")


if __name__ == "__main__":
    sys.exit(main())
