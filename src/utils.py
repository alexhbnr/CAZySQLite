########################################################################
# Utility functions
#
# Alex Huebner, 26/03/2020
########################################################################

import os


def create_dirs(fn):
    """Create missing directories for output fn."""
    if not os.path.isdir(os.path.dirname(fn)) and os.path.dirname(fn) != "":
        os.makedirs(os.path.dirname(fn), exist_ok=True)


