# scd

**This is WIP project, so please check this repo after 0.1 release. Before
this release, dragons are everywhere.**

scd (something completely different) is yet another bumpversion
implementation. Of course, there are several available implementations
available in the wild and you have a question: WHY THE HELL ON THE WORLD
DO I NEED ANOTHER ONE. Legit question.

Most bumpversion implementation are rather simple. They are just
wrappers for sed and could be replaced by sed itself. Seriously, all
these projects can be implemented as shell script with sed/awk mess in
20-30 lines. This project can be implemented in ~50 lines.

I tried to use more or less all bumpversions I can found in the wild and
most of them are not suitable for my projects. The reason is that they
are really simple. They works great if you have a project with 1 library
(maybe 2). But if you have repository with 8-10 libraries (let's say,
API, workers and plugins) it becomes a mess. You need to maintain huge
``.bumpversion.cfg`` and this construction is not really robust. Also,
almost all such projects do not know about development versions, most of
them just do not allow user to have several replacement rules for 1 file
(yes, sometimes you need that).

scd has a config file named ``.scd.yaml`` (or ``.scd.json``,
``scd.toml``) which allows you to set current version of your project
with development, post releases etc. If you do not need such complexity,
please feel free to use other projects (I insist: keep simpliest tools
if possible, whilist it is not nightmare to use them).

Btw, the name. Every version bumping is kinda "and hopefully this time,
we could both make it right.". And every release looks like that:

[![IMAGE ALT TEXT](http://img.youtube.com/vi/FGK8IC-bGnU/0.jpg)](https://www.youtube.com/watch?v=FGK8IC-bGnU)
