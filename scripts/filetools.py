"""Tools for files.  """

import os

__dirname__ = os.path.abspath(os.path.dirname(__file__))

def workspace_path(*other):

    return os.path.join(os.path.dirname(__dirname__), *other)

