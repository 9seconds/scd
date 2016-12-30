Usage
=====

CLI Arguments and Options
-------------------------

::

   usage: scd [-h] [-V] [-p] [-n] [-c CONFIG_PATH]
              [-x [CONTEXT_VAR [CONTEXT_VAR ...]]] [-d | -v]
              [FILE_PATH [FILE_PATH ...]]

   scd is a tool to manage version strings within your project files.

   positional arguments:
     FILE_PATH             Path to the files where to make version bumping. If
                           nothing is set, all filenames in config will be used.

   optional arguments:
     -h, --help            show this help message and exit
     -V, --own-version     print version only.
     -p, --replace-version
                           print version to replace to.
     -n, --dry-run         make dry run, do not change anything.
     -c CONFIG_PATH, --config CONFIG_PATH
                           path to the config. By default autodiscovery will be
                           performed.
     -x [CONTEXT_VAR [CONTEXT_VAR ...]], --extra-context [CONTEXT_VAR [CONTEXT_VAR ...]]
                           Additional context variables. Format is key=value.
     -d, --debug           run in debug mode
     -v, --verbose         run tool in verbose mode

I have no idea what to add here. You can get this output with ``scd -h``.


Debug and Verbose Mode
----------------------

By default, scd won't notify you about anything. And won't print. But
somethimes you want to know about some details. There are 2 ways how to
do that: using debug and verbose mode.

Verbose output should be used if you are worrying about how scd is
processing your files. Debug output - if you have some issue and want
to yell on developer having something in your hands. If suspect you
absolutely do not need to execute debug mode if you are not author of
the tool.

Here are examples:

**Verbose mode**:

::

   >>> Use /home/sergey/dev/pvt/scd/.scd.yaml as config file
   >>> Parsed config as YAML
   >>> Version is 0.1.0.dev24+3177b4e
   >>> Start to process /home/sergey/dev/pvt/scd/setup.py
   >>> Modify 'version="0.0.1",' to 'version="0.1.0.dev24+3177b4e",'
   >>> Start to process /home/sergey/dev/pvt/scd/docs/source/conf.py
   >>> Modify "version = '1.0'" to "0.1'"
   >>> Modify "release = '1.0.0b1'" to "0.1.0'"
   >>> Start to process /home/sergey/dev/pvt/scd/scd/__init__.py
   >>> Modify '__version__ = "0.1.0"' to '0.1.0.dev24"'

**Debug mode**:

::

   149 [DEBUG  ] (      main:69 ) Options: Namespace(config=None, debug=True, dry_run=True, files=[], verbose=False)
   149 [DEBUG  ] (      main:169) Search configfile in /home/sergey/dev/pvt/scd
   149 [INFO   ] (      main:177) Use /home/sergey/dev/pvt/scd/.scd.yaml as config file
   150 [DEBUG  ] (    config:197) Use default json as JSON config parser.
   164 [DEBUG  ] (    config:218) Use PyYAML for YAML config parser.
   165 [DEBUG  ] (    config:228) Use toml for TOML config parser.
   165 [DEBUG  ] (    config:244) Cannot parse JSON: Expecting value: line 1 column 1 (char 0)
   169 [INFO   ] (    config:240) Parsed config as YAML
   169 [DEBUG  ] (    config:242) Parsed config content:
   {
       "defaults": {
           "replacement": "full",
           "search": "pep440"
       },
       "files": {
           "docs/source/conf.py": [
               {
                   "replace_raw": "{{ major }}.{{ minor }}",
                   "search_raw": "^version\\s=\\s'{{ pep440 }}'"
               },
               {
                   "replace_raw": "{{ major }}.{{ minor }}.{{ patch }}",
                   "search_raw": "^release\\s=\\s'{{ pep440 }}'"
               }
           ],
           "scd/__init__.py": [
               {
                   "replace_raw": "{{ major }}.{{ minor }}.{{ patch }}{% if post %}.post{{ post }}{% endif %}{% if dev %}.dev{{ dev }}{% endif %}",
                   "search_raw": "^__version__\\s=\\s\"{{ pep440 }}\""
               }
           ],
           "setup.py": [
               {
                   "replace": "full",
                   "search": "setuppy"
               }
           ]
       },
       "search_patterns": {
           "setuppy": "(?<=version=\\\"){{ git_pep440 }}"
       },
       "version": {
           "number": "0.1.0",
           "scheme": "git_pep440"
       }
   }
   175 [INFO   ] (      main:72 ) Version is 0.1.0.dev24+3177b4e
   176 [DEBUG  ] (     files:204) File /home/sergey/dev/pvt/scd/docs/source/conf.py is ok
   176 [DEBUG  ] (     files:204) File /home/sergey/dev/pvt/scd/setup.py is ok
   176 [DEBUG  ] (     files:204) File /home/sergey/dev/pvt/scd/scd/__init__.py is ok
   176 [INFO   ] (      main:81 ) Start to process /home/sergey/dev/pvt/scd/docs/source/conf.py
   176 [DEBUG  ] (      main:82 ) File object: <File(filename='docs/source/conf.py', path='/home/sergey/dev/pvt/scd/docs/source/conf.py', patterns=[<SearchReplace(search="^version\\s=\\s'v?\n    (?:\n        (?:(?P<epoch>[0-9]+)!)?                           # epoch\n        (?P<release>[0-9]+(?:\\.[0-9]+)*)                  # release segment\n        (?P<pre>                                          # pre-release\n            [-_\\.]?\n            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))\n            [-_\\.]?\n            (?P<pre_n>[0-9]+)?\n        )?\n        (?P<post>                                         # post release\n            (?:-(?P<post_n1>[0-9]+))\n            |\n            (?:\n                [-_\\.]?\n                (?P<post_l>post|rev|r)\n                [-_\\.]?\n                (?P<post_n2>[0-9]+)?\n            )\n        )?\n        (?P<dev>                                          # dev release\n            [-_\\.]?\n            (?P<dev_l>dev)\n            [-_\\.]?\n            (?P<dev_n>[0-9]+)?\n        )?\n    )\n    (?:\\+(?P<local>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*))?       # local version'", replace=<Template memory:7f92ac61bc50>)>, <SearchReplace(search="^release\\s=\\s'v?\n    (?:\n        (?:(?P<epoch>[0-9]+)!)?                           # epoch\n        (?P<release>[0-9]+(?:\\.[0-9]+)*)                  # release segment\n        (?P<pre>                                          # pre-release\n            [-_\\.]?\n            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))\n            [-_\\.]?\n            (?P<pre_n>[0-9]+)?\n        )?\n        (?P<post>                                         # post release\n            (?:-(?P<post_n1>[0-9]+))\n            |\n            (?:\n                [-_\\.]?\n                (?P<post_l>post|rev|r)\n                [-_\\.]?\n                (?P<post_n2>[0-9]+)?\n            )\n        )?\n        (?P<dev>                                          # dev release\n            [-_\\.]?\n            (?P<dev_l>dev)\n            [-_\\.]?\n            (?P<dev_n>[0-9]+)?\n        )?\n    )\n    (?:\\+(?P<local>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*))?       # local version'", replace=<Template memory:7f92ac61bcf8>)>])>
   184 [INFO   ] (     files:61 ) Modify "version = '1.0'" to "0.1'"
   185 [INFO   ] (     files:61 ) Modify "release = '1.0.0b1'" to "0.1.0'"
   186 [DEBUG  ] (      main:149) No need to save /home/sergey/dev/pvt/scd/docs/source/conf.py
   186 [INFO   ] (      main:81 ) Start to process /home/sergey/dev/pvt/scd/setup.py
   186 [DEBUG  ] (      main:82 ) File object: <File(filename='setup.py', path='/home/sergey/dev/pvt/scd/setup.py', patterns=[<SearchReplace(search='(?<=version=\\")v?\n    (?:\n        (?:(?P<epoch>[0-9]+)!)?                           # epoch\n        (?P<release>[0-9]+(?:\\.[0-9]+)*)                  # release segment\n        (?P<pre>                                          # pre-release\n            [-_\\.]?\n            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))\n            [-_\\.]?\n            (?P<pre_n>[0-9]+)?\n        )?\n        (?P<post>                                         # post release\n            (?:-(?P<post_n1>[0-9]+))\n            |\n            (?:\n                [-_\\.]?\n                (?P<post_l>post|rev|r)\n                [-_\\.]?\n                (?P<post_n2>[0-9]+)?\n            )\n        )?\n        (?P<dev>                                          # dev release\n            [-_\\.]?\n            (?P<dev_l>dev)\n            [-_\\.]?\n            (?P<dev_n>[0-9]+)?\n        )?\n    )\n    (?:\\+(?P<local>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*))?       # local version', replace=<Template memory:7f92ac60d9b0>)>])>
   193 [INFO   ] (     files:61 ) Modify 'version="0.0.1",' to 'version="0.1.0.dev24+3177b4e",'
   193 [DEBUG  ] (      main:149) No need to save /home/sergey/dev/pvt/scd/setup.py
   193 [INFO   ] (      main:81 ) Start to process /home/sergey/dev/pvt/scd/scd/__init__.py
   193 [DEBUG  ] (      main:82 ) File object: <File(filename='scd/__init__.py', path='/home/sergey/dev/pvt/scd/scd/__init__.py', patterns=[<SearchReplace(search='^__version__\\s=\\s"v?\n    (?:\n        (?:(?P<epoch>[0-9]+)!)?                           # epoch\n        (?P<release>[0-9]+(?:\\.[0-9]+)*)                  # release segment\n        (?P<pre>                                          # pre-release\n            [-_\\.]?\n            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))\n            [-_\\.]?\n            (?P<pre_n>[0-9]+)?\n        )?\n        (?P<post>                                         # post release\n            (?:-(?P<post_n1>[0-9]+))\n            |\n            (?:\n                [-_\\.]?\n                (?P<post_l>post|rev|r)\n                [-_\\.]?\n                (?P<post_n2>[0-9]+)?\n            )\n        )?\n        (?P<dev>                                          # dev release\n            [-_\\.]?\n            (?P<dev_l>dev)\n            [-_\\.]?\n            (?P<dev_n>[0-9]+)?\n        )?\n    )\n    (?:\\+(?P<local>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*))?       # local version"', replace=<Template memory:7f92ac61ff98>)>])>
   198 [INFO   ] (     files:61 ) Modify '__version__ = "0.1.0"' to '0.1.0.dev24"'
   198 [DEBUG  ] (      main:149) No need to save /home/sergey/dev/pvt/scd/scd/__init__.py


Dry Run
-------

Sometimes you do not want to do replacement, but to check what it will
change. Execute scd with ``--dry-run`` flag. Also, I advise to run in
verbose mode to get details you want.


Config Autodiscovery
--------------------

It is always possible to set path to your config with ``--config``. It
is fine but sometimes you do not want to remember where is your config
is placed. And you are working within Git repository. And all folks are
placing such files in the root of repositories so... this is idea of
autodiscovery.

Let's assume that you are working in :file:`./ui` directory of
your repository and execuing scd without explicit config path
(:file:`--config ../.scd.yaml`). What will happen:

#. scd will try to search within your current directory. It will search
   configs in following order:

   * :file:`.scd.json`
   * :file:`scd.json`
   * :file:`.scd.yaml`
   * :file:`scd.yaml`
   * :file:`.scd.toml`
   * :file:`scd.toml`
#. If nothing is found, scd will get top level of your repository (``git
   rev-parse --show-toplevel``) and start to search there. The same file
   order.


Extra Context
-------------

Sometimes you need to have some extra context to propagate
into templates or patterns. Here is the flag for that, ``-x``
(``--extra-context``). If you execute scd like ``scd -x name=myname``,
you will get ``name`` variable for replacement and search patterns
immediately.
