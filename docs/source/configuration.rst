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

  {
      "$schema": "http://json-schema.org/draft-04/schema",
      "type": "object",
      "required": ["version", "files"],
      "properties": {
          "version": {
              "type": "object",
              "required": ["scheme", "number"],
              "properties": {
                  "scheme": {
                      "type": "string",
                      "enum": ["pep440", "git_pep440", "semver", "git_semver"]
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

Files are the list of file structures which scd should worry about. Each
structure looks like this:


Predefined Template Context
+++++++++++++++++++++++++++

Search Context
--------------

Replacement Context
-------------------

SemVer
******

PEP440
******
