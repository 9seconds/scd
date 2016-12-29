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


License and Legal Stuff
+++++++++++++++++++++++

Software is distributed using `MIT license
<https://tldrlegal.com/license/mit-license>`_.

::

   MIT License

   Copyright (c) 2016 Sergey Arkhipov

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.

You can find source codes on GitHub: https://github.com/9seconds/scd.


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
