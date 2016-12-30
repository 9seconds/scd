# -*- coding: utf-8 -*-
""":abbr:`scd (Something Completely Different)`.

This is yet another implementation of the tools called bumpversions.
There are many such tools available in the wild and I thoroughly
looked through them. And decided to reinvent the wheel. You have a
legit question: WHY THE BLOODY HELL DOES THIS WORLD NEED YET ANOTHER
BUMPVERSION? Because I wanted the tool which works better at slightly
bigger scale and I wanted the tool which I won't fight against
immediately after adoption.

All bumpversion-like tools alllow you to manage versions of your
software within a project. If you have a version number in your config
file, documentation title, somewhere in the code, you know that it is
irritating to update them manually to the new version. So there is whole
set of tools which can manage them with one command.

For example, there is well-known and probably standard de-facto
`bumpversion <https://github.com/peritus/bumpversion>`_. Unfortunately,
bumpversion seems stale and seriously limited in its capabilities
(this is the main reason why scd was born). For example, there are no
regular expressions and replacement patterns look cumbersome (why do
we need that ``serialize`` block if we can use templates? Templates
are everywhere!). Also, I wanted to have a possibility to use several
replacement blocks without dancing around INI syntax which never works
on practice (probably I tend to complicate things, but with bigger
project INI starts to irritate a lot).

scd is extensible with `setuptools' entrypoints
<http://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points>`_.
It basically means that if you want, you can always create you own
implementation of some functions, scd will discover that and can use.

Currently, there is only one entrypoint is defined, ``scd.version``.
All instances of that entrypoint should be subclasses
of :py:class:`scd.version.Version` class. Please check
:py:class:`scd.version.SemVer` or :py:class:`scd.version.PEP440` for
examples.
"""


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


try:
    import colorama
except ImportError:
    pass
else:
    colorama.init(autoreset=True)


__version__ = "1.0.0"
__version__ = __version__.split(".")
"""Identifier of the current version.

Basically, this is a tuple like :py:data:`sys.version_info`, but not
named one. For example, if version is *0.1.0*, then ``__version__ ==
("0", "1", "0")``.
"""
