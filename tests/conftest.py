"""pytest config"""

import os
import sys

__dirname__ = os.path.abspath(os.path.dirname(__file__))


def _file_path(*other):

    return os.path.abspath(os.path.join(__dirname__, *other))


def pytest_configure(config):
    sys.path.insert(0, _file_path('..'))
    return config
