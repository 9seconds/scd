# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


try:
    import colorama
except ImportError:
    pass
else:
    colorama.init(autoreset=True)


# TODO(9seconds): Make paths in config files idempotent to OS
__version__ = "0.1.0"
__version__ = __version__.split(".")
