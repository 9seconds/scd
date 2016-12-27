Usage
=====

CLI Arguments and Options
-------------------------

::

   usage: scd [-h] [-d] [-v] [-n] [-c CONFIG_PATH] [FILE_PATH [FILE_PATH ...]]

   scd is a tool to manage version strings within your project files.

   positional arguments:
     FILE_PATH             Path to the files where to make version bumping. If
                           nothing is set, all filenames in config will be used.

   optional arguments:
     -h, --help            show this help message and exit
     -d, --debug           run in debug mode
     -v, --verbose         run tool in verbose mode
     -n, --dry-run         make dry run, do not change anything.
     -c CONFIG_PATH, --config CONFIG_PATH
                           Path to the config. By default autodiscovery will be
                           performed.

   Please check GH of the SCD for issues and updates:
   https://github.com/9seconds/scd


Debug and Verbose Mode
----------------------

Dry Run
-------

Config Autodiscovery
--------------------
