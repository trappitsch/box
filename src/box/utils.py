# Utility and helper functions

from contextlib import contextmanager
import os
from pathlib import Path
import subprocess

from rich_click import ClickException

from box.config import PyProjectParser

# available app entry types that are used in box
PYAPP_APP_ENTRY_TYPES = ["spec", "module", "script", "notebook"]

# supported Python versions. Default will be set to last entry (latest).
PYAPP_PYTHON_VERSIONS = (
    "pypy2.7",
    "pypy3.9",
    "pypy3.10",
    "3.7",
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
)


def check_boxproject() -> None:
    """Check if the box project is already initialized."""
    check_pyproject()
    pyproj = PyProjectParser()
    if not pyproj.is_box_project:
        raise ClickException("This is not a box project. Initialize with `box init`.")


def check_pyproject() -> None:
    """Raise a click exception if a pyproject.toml file is not found."""
    if not Path("pyproject.toml").exists():
        raise ClickException("No pyproject.toml file found.")


def cmd_python() -> str:
    """Get the command to run Python on the current operating system.

    :return: Command to run Python
    """
    if is_windows():
        try:
            subprocess.run(
                ["py", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return "py"
        except FileNotFoundError:
            pass
    return "python"


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
