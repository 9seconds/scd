Configuration
=============

scd uses configuration file to get information on settings,
search/replacement patterns and files to manage.

As you got from :ref:`installation-install-from-cheese-shop`,
scd can parse `TOML <https://github.com/toml-lang/toml>`_, `YAML
<http://yaml.org/>`_ and `JSON <http://www.json.org>`_ configuration
files. So first we need to elaborate a little bit on how to create
required configuration.


Configuration Formats
+++++++++++++++++++++

Yes, 3 formats, but in most cases all three formats are possible to
reduce to equialent JSON. Here are examples of all 3 formats, which are
totally equialent.

**YAML**:

.. code-block:: yaml
  :linenos:

  version:
    number: 1.2.3
    scheme: semver

  search_patterns:
    full: "{{ full }}"

  replacement_patterns:
    full: "{{ full }}"

  defaults:
    search: full
    replace: full

  files:
    setup.py:
      - default

**TOML**:

.. code-block:: toml
  :linenos:

  [version]
  number = "1.2.3"
  scheme = "semver"

  [search_patterns]
  full = "{{ full }}"

  [replacement_patterns]
  full = "{{ full }}"

  [defaults]
  search = "full"
  replace = "full"

  [files]
  "setup.py" = ["default"]


**JSON**:

.. code-block:: json
  :linenos:

  {
      "version": {
          "number": "1.2.3",
          "scheme": "semver"
      },
      "search_patterns": {
          "full": "{{ full }}"
      },
      "replacement_patterns": {
          "full": "{{ full }}"
      },
      "defaults": {
          "search": "full",
          "replace": "full"
      },
      "files": {
          "setup.py": ["default"]
      }
  }

I hope you get an idea: all these formats are representing
the same datastructure. If you are familiar with `JSON Schema
<http://json-schema.org/>`_, you may find that useful:

.. code-block:: json
  :linenos:

  {
      "$schema": "http://json-schema.org/draft-04/schema",
      "type": "object",
      "required": ["version", "defaults", "files"],
      "properties": {
          "config": {
              "type": "number",
              "minimum": 1,
              "multipleOf": 1.0
          },
          "version": {
              "type": "object",
              "required": ["scheme", "number"],
              "properties": {
                  "scheme": {
                      "type": "string",
                      "enum": ["pep440", "semver", "git_pep440", "git_semver"]
                  },
                  "number": {
                      "oneOf": [
                          {"type": "number"},
                          {"type": "string"}
                      ]
                  }
              }
          },
          "files": {
              "type": "object",
              "additionalProperties": {
                  "type": "array",
                  "items": {
                      "oneOf": [
                          {"type": "string", "enum": ["default"]},
                          {
                              "type": "object",
                              "properties": {
                                  "search": {"type": "string"},
                                  "search_raw": {"type": "string"},
                                  "replace": {"type": "string"},
                                  "replace_raw": {"type": "string"}
                              },
                              "anyOf": [
                                  {
                                      "required": ["search"],
                                      "not": {"required": ["search_raw"]}
                                  },
                                  {
                                      "required": ["search_raw"],
                                      "not": {"required": ["search"]}
                                  },
                                  {
                                      "required": ["replace"],
                                      "not": {"required": ["replace_raw"]}
                                  },
                                  {
                                      "required": ["replace_raw"],
                                      "not": {"required": ["replace"]}
                                  }
                              ]
                          }
                      ]
                  }
              }
          },
          "search_patterns": {
              "type": "object",
              "additionalProperties": {"type": "string"}
          },
          "replacement_paterns": {
              "type": "object",
              "additionalProperties": {"type": "string"}
          },
          "groups": {
              "type": "object",
              "additionalProperties": {"type": "string"}
          },
          "defaults": {
              "type": "object",
              "properties": {
                  "search": {"type": "string"},
                  "replacement": {"type": "string"}
              },
              "additionalProperties": false
          }
      }
  }


Please be noticed that it is possible to extend allowed schemes with
external entrypoints but :pep:`440` and `SemVer <http://semver.org/>`_
are supported out of box.


Examples
++++++++

For simplicity, I will put examples here in YAML but as you already
understand, they could be easily made with any other format.


Full Example
------------

.. code-block:: yaml
  :linenos:

  config: 1

  version:
    number: 1.0.1
    scheme: semver

  search_patterns:
    full: "{{ semver }}"
    vfull: "v{{ semver }}"
    major_minor_block: "\\d+\\.\\d+(?=\\s\\#\\sBUMPVERSION)"

  replacement_patterns:
    full: "{{ full }}"
    major_minor: "{{ major }}.{{ minor }}"
    major_minor_p: "{{ major }}.{{ minor }}{% if patch %}.{{ patch }}{% endif %}"

  defaults:
    search: full
    replace: full

  groups:
    code: 'scd/.*?\.py'
    docs: 'docs/.*?'

  files:
    setup.py:
      - search_raw: "(?>=version\\s=\\s\\\"){{ full }}"
    docs/conf.py:
      - default
      - search: vfull
        replace: major_minor_p
      - search: major_minor_block
        replace_raw: "{{ next_major }}"


Shortest Example
----------------

.. code-block:: yaml
  :linenos:

  version:
    number: 1.0.1
    scheme: semver

  defaults:
    search: semver
    replace: base

  files:
    setup.py:
      - default

So, as you can see, config can be large and can be small. It is up to
you what to choose.



Parameters
++++++++++

From examples above you may get an idea that some parameters are
optionals, some mandatory. Mandatory parameters are ``version``,
``defaults`` and ``files``. All others are optionals.

Also, you may notice Mustache-like strings like ``{{ something }}``.
Your guessing is correct, it is `Jinja2 <http://jinja.pocoo.org/>`_
templates. Template context variables are depended on choosen version
scheme, you can get a list of them in `Predefined Template Context`_.


``config``
----------

``config`` is a numeric version (integers, please) of the config format.
This is the first field processed by scd therefore it is possible to
have absolutely different schemas in future.

This field is responsible for config schema version. Sometimes (probably
in future) we will bring (definitely will) some non-backward compatible
changes in schema and we will differ configs by numbers.

This field is optional in 1.x versions, it implicitly equal to 1.


``version``
-----------

Version block defines a settings, related to versioning strategy.

scd won't calculate version for you, you need to set base version
by your own. Some may consider that as inconvenience (if you have
latest version 0.1.0, it is good to have next one as 0.1.1 calculated
automatically), but I belive this is for the greatest good (struggling
to force your smartass versioner to have next version 0.2 is way more
inconvenient, than setting explicit one).

This block has 2 mandatory parameters and 0 optionals.

+-----------+--------+---------+-------------------------------------------------------------------------------------+
| Parameter | Type   | Example | Description                                                                         |
+===========+========+=========+=====================================================================================+
| number    | string | 1.2.3   | This parameter defines basic version you are developing. Upcoming planned           |
|           |        |         | version.                                                                            |
|           |        |         |                                                                                     |
|           |        |         | For example, you've just released version 1.3.0. What is the next version?          |
|           |        |         | Basically, nobody knows. It might be 1.3.1, it might be 1.4.0 or even 2.0.0.        |
|           |        |         | Seriously, it is totally up to your release management and branching strategy.      |
|           |        |         | This number is *planned* version, not *released* one. Planned.                      |
|           |        |         |                                                                                     |
|           |        |         | And all versions, calculated by scd will use that number as a base. So in templates |
|           |        |         | you may find ``{{ major }}`` as ``1``, ``{{ minor }}`` as ``2`` etc.                |
+-----------+--------+---------+-------------------------------------------------------------------------------------+
| scheme    | string | semver  | The name of the scheme your are using for versioning.                               |
|           |        |         |                                                                                     |
|           |        |         | scd will parse version numbers according to that parameter. So, all these           |
|           |        |         | ``major``, ``minor`` etc won't appear magically, they coming from parsed            |
|           |        |         | ``version/number`` parameter. Please check `Predefined Template Context`_ to get a  |
|           |        |         | list of parsed context variables.                                                   |
|           |        |         |                                                                                     |
|           |        |         | by default, scd supports :pep:`440` and `semver`_ schemes. Their codenames are      |
|           |        |         | ``pep440`` and ``semver`` accordingly. Also, there are Git-flavored schemes         |
|           |        |         | ``git_pep440`` and ``git_semver``: these flavors more or less the same as their     |
|           |        |         | prefixless variants, but scd will use git to calculate some parameters like         |
|           |        |         | putting git tag in local part of :pep:`440` or distance from latest version tag as  |
|           |        |         | prerelase in semver.                                                                |
|           |        |         |                                                                                     |
|           |        |         | User can define his own schemes using entrypoints-based plugin mechanism. Please    |
|           |        |         | check documentation for :py:mod:`scd.version` for that.                             |
+-----------+--------+---------+-------------------------------------------------------------------------------------+


``search_patterns``
-------------------

Search patterns defines regular expression which are used to search a
place in file where to replace.

scd works in line-mode fashion, similar to sed, so all
expressions applied to the line. Also, please be noticed that
due to some implementation details, all expression will be
compiled with :py:data:`re.VERBOSE` and :py:data:`re.UNICODE`.
If you are not from Python world, please check `re
<https://docs.python.org/3/library/re.html>`_ documentation.

.. important::

    Please check documentation on `re.VERBOSE <https://docs.python.org/3/library/re.html#re.VERBOSE>`_. Seriously, if you do not know what it is, go and read.

This block should have a simple mapping, where key is the name of the
pattern and value is regular expression, understandable by Python.

There are several predefined search templates are available:

* ``pep440``
* ``semver``
* ``git_pep440``
* ``git_semver``

They are matching version in the format, allowed by semver or PEP440. If
you have your own versioning available as plugin, it will be here also.
Since all of them are defined, there is no need to define them on your
own. But if you define pattern with such name in that section, default
one will be, obviously, overriden.

Also, to simplify composition of your own patterns, these names are
available as template context variables in search patterns. In other
words, pattern like ``v{{ semver }}`` is perfectly fine.

.. important::

    scd will replace group 0 of the pattern. This is done intentionally
    to avoid possible ambiguity. In other word, it replaces whole
    pattern, not only some group. If you want to define regular
    expression more presicely, please use look-ahead and look-behind
    expressions.


``replacement_patterns``
------------------------

Replacement patterns are used to express version for the search pattern.

The same thing, this parameter is key/value mapping where key if the
name of the pattern and value is Jinja2 template, used for replacement.
For available context variables please check `PEP440`_ and `SemVer`_

There are 2 predefined replacement patterns:

+------+------------+-----------------------------------------------------------+
| Name | Equialent  | Description                                               |
+======+============+===========================================================+
| base | {{ base }} | Base version. Literally, the same stuff as you have in    |
|      |            | `version/number` block                                    |
+------+------------+-----------------------------------------------------------+
| full | {{ full }} | Full version, generated by your scheme. The most complete |
|      |            | and precise as possible.                                  |
+------+------------+-----------------------------------------------------------+

Of course, it is possible to override them in that section.


``groups``
----------

Sometimes you want to change versions only in some subset of files.
This why you can group them in some optional groups and filter by these
groups. So, let's say you've defined groups *code* and *docs*. In that
case, you can modify versions in docs only, without touching the code.

This is a mapping parameter. Key is the group name, value is regular
expression. Each expression sets a path (or pathes) relative to the
position of config file. The same story, as in `files`_.

.. important::

    scd will implicitly append ``$`` to the pattern. Please do not use
    ``^`` and ``$`` as start/end of the line - it just makes no sense.


``defaults``
------------

If you have a lot of files, sometimes you want to have some default
replacement or search. This is because it is possible to postpone some
parameter having default one.

This block has 2 mandatory parameters and 2 optionals.

+---------+--------------------------------------------------------------------------+
| Name    | Description                                                              |
+=========+==========================================================================+
| search  | This is a name of search pattern which should be used by default.        |
+---------+--------------------------------------------------------------------------+
| replace | This is a name of default replacement pattern should be used by default. |
+---------+--------------------------------------------------------------------------+

Please be noticed, that values are *names*, not raw patterns. Keys from
``search_patterns`` and ``replacement_patterns``.


``files``
---------

Files are the list of file structures which scd should worry about. If
scd does not have a section in config file, it will ignore file even
if it explicitly set in CLI. Well, because nobody knows how to manage
unknown file.

This is a mapping between filenames and a list of search/replacements.

Filename is rather simple: it is POSIX path to the file, relative
to the config. POSIX means that separator is ``/``, not ``\``.
So if you have a filename :file:`docs/source/conf.py`, it will
work perfectly on Unix/OS X and Windows. On Windows, actually, scd
will interpret this path as :file:`docs\source\conf.py` os it is
crossplatform. Another mentioned thing about filename is that it
is relative to the config file. So with file above and config file
path :file:`/home/username/project/.scd.yaml`, scd will process
:file:`/home/username/project/docs/source/conf.py`.

Search/replacements are the list with following rules:

+-------------+---------------------------------------------------------------------------------------------+
| Parameter   | Description                                                                                 |
+=============+=============================================================================================+
| search      | The *name* of the search pattern from ``search_patterns`` or some globally defined.         |
|             |                                                                                             |
|             | Please check `search_patterns`_ for details.                                                |
|             |                                                                                             |
|             | **Note**: this is mutually exclusive with ``search_raw``. Please define either              |
|             | ``search`` or ``search_raw``.                                                               |
+-------------+---------------------------------------------------------------------------------------------+
| search_raw  | The *pattern* to use. This is actual regular expression which can be used to define         |
|             | some search pattern ad-hoc, without populating ``search_patterns`` section with             |
|             | patterns which require only once.                                                           |
|             |                                                                                             |
|             | Please check `search_patterns`_ for details on how to compose such regular expressions.     |
|             |                                                                                             |
|             | **Note**: this is mutually exclusive with ``search``. Please define either ``search``       |
|             | or ``search_raw``.                                                                          |
+-------------+---------------------------------------------------------------------------------------------+
| replace     | The *name* of the replacement pattern from ``replacement_patterns`` or some globally        |
|             | defined.                                                                                    |
|             |                                                                                             |
|             | Please check `replacement_patterns`_ for details.                                           |
|             |                                                                                             |
|             | **Note**: this is mutually exclusive with ``replace_raw``. Please define either             |
|             | ``replace`` either ``replace_raw``                                                          |
+-------------+---------------------------------------------------------------------------------------------+
| replace_raw | The *replacement* template to use. This is actual Jinja2 template which can be used         |
|             | to define some ad-hoc replacement without populating ``replacement_patterns`` section       |
|             | with stuff which require only once.                                                         |
|             |                                                                                             |
|             | Please check `replacement_patterns`_ for details.                                           |
|             |                                                                                             |
|             | **Note**: this is mutually exclusive with ``replace``. Please define either ``replace_raw`` |
|             | either ``replace``.                                                                         |
+-------------+---------------------------------------------------------------------------------------------+

Please be noticed that at least something has to be defined. You may
postpone any parameter (no ``search`` or ``search_raw`` for example,
but if you define any, please remember about mutual exclusive groups,
mentioned in table), then parameters from `defaults`_ section will
be used. But do not keep element empty. There is special placeholder
``default`` for that. So if you want to use defaults only, please use
config like:

.. code-block:: yaml
  :linenos:

  version:
    number: 1.0.1
    scheme: semver

  defaults:
    search: semver
    replace: base

  files:
    setup.py:
      - default

In that case ``semver`` search pattern and ``base`` replacement will be
used for :file:`setup.py`.


Predefined Template Context
+++++++++++++++++++++++++++

As it was previously mentioned, there are several predefined context
variables which might be used in templates for search and replacements.
Also, please remember, that these contexts are different: you cannot use
context vars from replacements to make search pattern.

Search Context
--------------

+------------------+----------------------------------------------------------------------------------+
| Context Variable | Description                                                                      |
+==================+==================================================================================+
| pep440           | This searches version number, valid according to :pep:`440`.                     |
+------------------+----------------------------------------------------------------------------------+
| git_pep440       | Same as ``pep440``.                                                              |
+------------------+----------------------------------------------------------------------------------+
| semver           | This searches version number, valid according to `semver <http://semver.org/>`_. |
+------------------+----------------------------------------------------------------------------------+
| git_semver       | Same as ``semver``.                                                              |
+------------------+----------------------------------------------------------------------------------+


Replacement Context
-------------------

Replacement context is totally dependend on version scheme provided.
Moreover, every scheme provides its own set of context variables, and
it is possible that you have a scheme which is not version numbered (I
worked with such scheme once, and it was not that bad as one can think).

Of course, there is a number of some predefined context variables for
replacements, you may find them in `replacement_patterns`_ section.

For next sections we need to make some assumptions on versions.
Let's pretend that we have version ``1.2.0`` in our config
file, using Git flavor of a scheme, operating on commit
``ff5cff170e93ab4f7dd87437951c6646e297c538`` which is 5 commits left
from latest version tag.


SemVer
******

+------------------+---------+--------------------+
| Context Variable | Type    | Value From Example |
+==================+=========+====================+
| base             | string  | 1.2.0              |
+------------------+---------+--------+-----------+
| full             | string  | 1.2.0-5+ff5cff1    |
+------------------+---------+--------------------+
| major            | integer | 1                  |
+------------------+---------+--------------------+
| next_major       | integer | 2                  |
+------------------+---------+--------------------+
| prev_major       | integer | 0                  |
+------------------+---------+--------------------+
| minor            | integer | 2                  |
+------------------+---------+--------------------+
| next_minor       | integer | 3                  |
+------------------+---------+--------------------+
| prev_minor       | integer | 1                  |
+------------------+---------+--------------------+
| patch            | integer | 0                  |
+------------------+---------+--------------------+
| next_patch       | integer | 1                  |
+------------------+---------+--------------------+
| prev_patch       | integer | 0                  |
+------------------+---------+--------------------+
| prerelase        | string  | 5                  |
+------------------+---------+--------------------+
| next_prerelease  | string  | 6                  |
+------------------+---------+--------------------+
| prev_prerelease  | string  | 4                  |
+------------------+---------+--------------------+
| build            | string  | ff5cff1            |
+------------------+---------+--------------------+
| next_build       | string  | ff5cff2            |
+------------------+---------+--------------------+
| prev_build       | string  | ff5cff0            |
+------------------+---------+--------------------+

As you can see, this is rather trivial. The most interesting parts are
build and prerelase management. By default, scd will try to guess next
and previous parts (it increments latest number found in the string).
Sometimes it make sense (``build5`` for example), sometimes not (Git
commit hash) so please pay attention to your strategy.


PEP440
******

To show all possible values, let's consider base version as ``1.2.0rc1``.

+------------------+---------+-------------------------------+
| Context Variable | Type    | Value From Example            |
+==================+=========+===============================+
| base             | string  | 1.2.0rc1                      |
+------------------+---------+--------------+----------------+
| full             | string  | 1.2.0rc1.dev5+ff5cff1         |
+------------------+---------+----------------------+--------+
| maximum          | string  | 0!1.2.0rc1.post0.dev5+ff5cff1 |
+------------------+---------+-------------------------------+
| epoch            | integer | 0                             |
+------------------+---------+-------------------------------+
| major            | integer | 1                             |
+------------------+---------+-------------------------------+
| next_major       | integer | 2                             |
+------------------+---------+-------------------------------+
| prev_major       | integer | 0                             |
+------------------+---------+-------------------------------+
| minor            | integer | 2                             |
+------------------+---------+-------------------------------+
| next_minor       | integer | 3                             |
+------------------+---------+-------------------------------+
| prev_minor       | integer | 1                             |
+------------------+---------+-------------------------------+
| patch            | integer | 0                             |
+------------------+---------+-------------------------------+
| next_patch       | integer | 1                             |
+------------------+---------+-------------------------------+
| prev_patch       | integer | 0                             |
+------------------+---------+-------------------------------+
| prerelase        | integer | 1                             |
+------------------+---------+-------------------------------+
| prerelase_type   | string  | rc                            |
+------------------+---------+-------------------------------+
| next_prerelease  | integer | 2                             |
+------------------+---------+-------------------------------+
| prev_prerelease  | integer | 0                             |
+------------------+---------+-------------------------------+
| dev              | integer | 5                             |
+------------------+---------+-------------------------------+
| next_dev         | integer | 6                             |
+------------------+---------+-------------------------------+
| prev_dev         | integer | 4                             |
+------------------+---------+-------------------------------+
| post             | integer | 0                             |
+------------------+---------+-------------------------------+
| next_post        | integer | 1                             |
+------------------+---------+-------------------------------+
| prev_post        | integer | 0                             |
+------------------+---------+-------------------------------+
| local            | string  | ff5cff1                       |
+------------------+---------+-------------------------------+

So, more or less the same. The only difference is that ``full`` won't
display data which is 0 or empty. ``maximum`` does.
