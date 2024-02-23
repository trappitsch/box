# Utility and helper functions

from contextlib import contextmanager
import os
from pathlib import Path


def cmd_python() -> str:
    """Get the command to run Python on the current operating system.

    :return: Command to run Python
    """
    return "py" if is_windows() else "python"


def is_windows() -> bool:
    """Check if the operating system is Windows.

    :return: True if Windows, False otherwise
    """
    return os.name == "nt"


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
