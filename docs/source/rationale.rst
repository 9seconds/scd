Rationale
=========

scd was created when I worked on project which is slightly better
than simple library. This project has several services (you
may add "micro" prefix if you want) and a lot of plugins. This
project has so many plugins that we even created `cookiecutter
<https://github.com/audreyr/cookiecutter>`_ template for that. Overall
more than 10 Python packages.

These packages have dependencies and some of these dependencies were
project dependencies. Such as common and some api package depend on
common, you get it. And we have to pin version or put a range like
``>=,<`` or ``~=`` (at that time pip/setuptools even do not understand
``~=``). Also, we had documentation and we had to manage documentation
via long running stable branches. So we had to support docs for version
1.0 and 2.0. Oh, and we had DEBs/RPMs and later Docker images where we
put versions in labels!

As you understand, version numbers were hardcoded everywhere. In some
places this was the only way to put version number (like in this doc).

We'd been trying to use `bumpversion
<https://github.com/peritus/bumpversion>`_. If worked fine for
some files but become a nightmare if we wanted to make complicated
replacement where regular expression will fit best. Also, it was totally
impossible to use bumpversion for files where we have to put ranges like
``dep>={major}.{minor},<{major}.{next_minor}`` (no next_minor, what a
pity). Yes, these files were not understand ``~=`` at that time and
please remember that not all package managers recognize such concept. It
had no regular expressions and several replacements for a file. We could
fork bumpversion but it was as complicated as create our own.

So here is rationale. We wanted bumpversion which:

#. Support several search/replacement pairs for a file
#. Support searching with regular expressions
#. Have a named sets of replacement/search patterns because in a lot of files these could repeat a lot
#. Have some default search/replacement pairs.
#. Have a more reasonable configuration format than INI.
#. Templates.
#. Possibility to set current version and understand that numbering in files can vary even if current development version persist.
#. Possibility to extract some information from Git to version numbers.

Let's elaborate on those items



Reasonable Configuration File
+++++++++++++++++++++++++++++

:program:`scd` has to support different configuration formats out of
box. Currently it supports JSON, YAML and TOML. These formats are not
ideal, but at least it is more reasonable to use them, then struggling
with INI limitations.

Also, there should be autodiscovery of such files. Please check
:doc:`configuration` to get more details.



Regular Expression Search
+++++++++++++++++++++++++

It was the biggest limit of bumpversion: using a literal string search.
Seriously, I do not want to keep precise literal structure of some
string in file. Developer who modifies the file, can forget about
:program:`bumpversion`, reindent things or replace some quotes from
single to doubles.

I do not want optional third-party tool to dictate how to keep precise
line in file. This irritates. That's why I need to have regular
expression search. Seriously, it is that simple. To have flexibility
to not remember about :program:`scd` or :program:`bumpversion` at all.
These tools are optional and should never be implicit dependencies.



Several Search/Replacement Pairs
++++++++++++++++++++++++++++++++

Okay, you have a package *X* which dependend on *Y* and *Z*. *X*, *Y*
and *Z* all are parts of your project. Fine, and you need to bump
version. Now solve problem: how to replace version range of *Y* and *Z*
in ``setup.py`` of *X*? In a single replacement literal pattern. Yes,
constant. Just because your version bumper is dumb enough to force you
to simplify its life. Or with giant unsupporable regexp, yes.

We need to have a support of multiple search/replacement pairs per file.
Dixi.



Named sets of Search/Replacement Pairs
++++++++++++++++++++++++++++++++++++++

If you have a lot of files where to manage version, you will quickly
realise that those files are not individual, you will have ~5-6
different search and replacement patterns overall. To avoid a long list
of copying and pasting, you need to have a possibility to assign pattern
with some name and use it later.

For example, you can have ``(?<=version\s=\s")\d+\.\d+\.\d+`` named as
``setuppy``. In that case, if you will replace double quotes with single
ones, you won't sed whole file, you can do it in one place.



Templates
+++++++++

Why the hell on the world do you need to implement confusing
``serialize`` blocks if world already has templates? :program:`scd` uses
`Jinja2 <http://jinja.pocoo.org/>`_ as templating engine.



Git and Development Releases
++++++++++++++++++++++++++++

We live in the world where development releases exist and we need
something to support them. It is great to have some base version for a
current developing release but we need to have a possiblity to generate
development version identifiers. Prerelases. Include build numbers.

In Python there are several projects to do that. For example, there is
widely used `pbr <http://docs.openstack.org/developer/pbr/>`_ which
generates development release numbers for you. There is `setuptools_scm
<https://github.com/pypa/setuptools_scm>`_ which is seriously great and
I highly recommend everyone to use it.

The only problem about setuptools-scm is its extensibility. It is
extendable by entrypoints and it is reasonable. But if you want to
have another version numbering policy, you need to implement your own
entrypoint. And put it somewhere. And set ``setup_requires`` to that
package. It works, but it is slightly inconvenient to use that, having
additional depenency you have to put somewhere and install before any
other package. But seriously, this project rocks. And available for
Python packages only so there is no way to update docs or RPM specs. And
it is irritating to have 2 schemes of versioning, they will fail one
day.
