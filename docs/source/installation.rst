Installation
============

:program:`scd` is simple Python package which hosted on `Cheese Shop
<https://pypi.python.org>`_ so if you are familiar with Python package
installation, it would be really straightforward.

Tool is using Python >= 2.7.


Prerequisites
+++++++++++++

To install scd, you need to have pip or setuptools installed. Pip is
required if you want to install it from Cheese Shop and setuptools if
you prefer source code installation.

To install `Pip <https://pip.pypa.io/en/stable/>`_ follow these guides:

* `Installation with package managers <https://packaging.python.org/install_requirements_linux/>`_
* `Installation without package managers <https://pip.pypa.io/en/stable/installing/>`_

To install setuptools follow `official guide
<http://setuptools.readthedocs.io/en/latest/setuptools.html#installing-setuptools>`_ and please check repository of your OS: there is a great possiblity that you already have it installed.


Install from Cheese Shop
++++++++++++++++++++++++

If you want to install system-wide or in virtualenv then do

.. code-block:: bash

    pip install scd

Otherwise, please do

.. code-block:: bash

    pip install --user scd


Install from sources
++++++++++++++++++++

.. code-block:: bash

   git clone https://github.com/9seconds/scd
   cd scd
   python setup.py install

Verify that tool is installed with ``scd --help``.
