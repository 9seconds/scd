And Now for Something Completely Different!
===========================================

|PyPI| |Build Status| |Code Coverage|

.. contents::
    :depth: 2
    :backlinks: none

scd (something competely different) is a small tool with one
intention: make your version bumping underoverengineered.
It takes slightly different approach than `bumpversion
<https://github.com/peritus/bumpversion>`_: it does not make commits or
tags and do not updates version by command. It takes configuration file
and adjust your version regarding this file.

It may seems a little bit complex, but it works really-really well if
you have a complex setup, where you need to manage versions not only in
literal format, but in different, complex ways in absolutely different
files. Also, it can eliminate a huge amount of copypasting in your
``.bumpversion.cfg``. Also, it works with regular expressions therefore
it can eliminate design restrictions of bumpversion.

Please check `official documentation <http://scd.readthedocs.io>`_ for
details. This README file is just a whirlwind tour.


Installation
++++++++++++

As any Python package, you can install scd with pip or sources.

.. code-block:: bash

    pip install scd[yaml,colors]

or

.. code-block:: bash

    git clone https://github.com/9seconds/scd
    cd scd
    python setup.py install


Configuration
+++++++++++++

Here is an example how can configuration file may looks like:

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

Yes, YAML! But you can use JSON or TOML also.

Mustaches are `Jinja2 <http://jinja.pocoo.org/>`_ templates (like in
`Ansible <https://www.ansible.com/>`_, for example). Also, as you can
see, it is possible to have a list of replacements per file.

And yes, versioning is done by schemes.

You can find a `thorough explanations
<http://scd.readthedocs.io/en/latest/configuration.html>`_ in docs.


Usage
+++++

Well, you would not belive, but

.. code-block:: bash

    scd

or more verbose

.. code-block:: bash

    scd -v
    >>> Use /home/sergey/dev/pvt/scd/.scd.yaml as config file
    >>> Parsed config as YAML
    >>> Version is 0.1.0.dev34+342f2c2
    >>> Start to process /home/sergey/dev/pvt/scd/setup.py
    >>> Modify 'version="0.0.1",' to 'version="0.1.0.dev34+342f2c2",'
    >>> Start to process /home/sergey/dev/pvt/scd/docs/source/conf.py
    >>> Modify "version = '1.0'" to "0.1'"
    >>> Modify "release = '1.0.0b1'" to "0.1.0'"
    >>> Start to process /home/sergey/dev/pvt/scd/scd/__init__.py
    >>> Modify '__version__ = "0.1.0"' to '0.1.0.dev34"'


Why scd?
++++++++

Because every version releases look the same.

.. image:: https://img.youtube.com/vi/FGK8IC-bGnU/0.jpg
    :alt: John Cleese on Something Completely Different
    :width: 560
    :target: https://www.youtube.com/watch?v=FGK8IC-bGnU

.. |PyPI| image:: https://img.shields.io/pypi/v/scd.svg
    :target: https://pypi.python.org/pypi/scd

.. |Build Status| image:: https://travis-ci.org/9seconds/scd.svg?branch=master
    :target: https://travis-ci.org/9seconds/scd

.. |Code Coverage| image:: https://codecov.io/gh/9seconds/scd/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/9seconds/scd
