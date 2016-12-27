And Now for Something Completely Different!
===========================================

:abbr:`scd (Something Completely Different)` is yet another
implementation of the tools called bumpversions. There are many such
tools available in the wild and I thoroughly looked through them. And
decided to reinvent the wheel. You have a legit question: WHY THE BLOODY
HELL DOES THIS WORLD NEED YET ANOTHER BUMPVERSION? Because I wanted the
tool which works better at slightly bigger scale and I wanted the tool
which I won't fight against immediately after adoption.

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

Please find more rants in :doc:`rationale`.


Why Something Completely Different?
+++++++++++++++++++++++++++++++++++

I usually find myself and my team in situation when we are over
optimistic about future releases. "This time we make things right". And
everytime, when we release, I feel myself as John Cleese:

.. raw:: html

    <div style="margin:2em 0;">
       <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/FGK8IC-bGnU" frameborder="0" allowfullscreen></iframe>
    </div>



Contents
++++++++

.. toctree::
   :maxdepth: 1

   rationale
   installation
   configuration
   usage
   api/index


Indices and tables
++++++++++++++++++

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
