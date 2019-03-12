"""Tools for files.  """

import os
__dirname__ = os.path.abspath(os.path.dirname(__file__))


def _file_path(*other):

    return os.path.abspath(os.path.join(__dirname__, *other))
