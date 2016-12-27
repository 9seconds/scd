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
     - filename: setup.py
       replacements:
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

   [[files]]
   filename = "setup.py"
   replacements = ["default"]


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
       "files": [
           {
               "filename": "setup.py",
               "replacements": [
                   "default"
               ]
           }
       ]
   }

I hope you get an idea: all these formats are representing
the same datastructure. If you are familiar with `JSON Schema
<http://json-schema.org/>`_, you may find that useful:

.. code-block:: json

   {
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
               "type": "array",
               "items": {
                   "type": "object",
                   "required": ["filename", "replacements"],
                   "properties": {
                       "filename": {"type": "string"},
                       "replacements": {
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
                                       }
                                   }
                               ]
                           }
                       }
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
     - filename: setup.py
       replacements:
         - search_raw: "(?>=version\\s=\\s\\\"){{ full }}"
     - filename: docs/conf.py
       replacements:
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
      - filename: setup.py
        replacements:
          - default

So, as you can see, config can be large and can be small. It is up to
you what to choose.

Parameters
++++++++++

``version``
-----------

``search_patterns``
-------------------

``replacement_patterns``
------------------------

``defaults``
------------

``files``
---------

Predefined Template Context
+++++++++++++++++++++++++++

Search Context
--------------

Replacement Context
-------------------
