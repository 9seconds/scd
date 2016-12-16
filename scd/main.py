# -*- coding: utf-8 -*-


import argparse
import logging
import sys


DESCRIPTION = """
scd is a tool to manage version strings within your project files.
"""
"""Description of the tool."""

EPILOG = """
Please check GH of the SCD for issues and updates:
https://github.com/9seconds/scd
"""
"""Epilog for the argparser."""


def main():
    options = get_options()
    configure_logging(options)


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
