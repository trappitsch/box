# Utility and helper functions

from contextlib import contextmanager
import os
from pathlib import Path


@contextmanager
def set_dir(dir: Path) -> None:
    """Context manager to change directory to a specific one and then go back on exit.

    :param dir: Folder to move to with `os.chdir`
    """
    origin = Path.cwd()
    try:
        os.chdir(dir)
        yield
    finally:
        os.chdir(origin)
