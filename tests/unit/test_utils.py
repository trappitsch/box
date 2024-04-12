# Test utility functions.

from pathlib import Path

import pytest
from rich_click import ClickException

import box.utils as ut


@pytest.mark.parametrize(
    "os_python",
    [["nt", "py"], ["posix", "python"]],
)
def test_cmd_python(mocker, os_python):
    """Get python on mulitple operating systems."""
    # mock os.name
    mocker.patch("os.name", os_python[0])
    mocker.patch("subprocess.run")
    assert ut.cmd_python() == os_python[1]


def test_cmd_python_py_not_found(mocker):
    """Default to python on windows if py not found."""
    mocker.patch("os.name", "nt")
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)
    assert ut.cmd_python() == "python"


def test_check_boxproject(rye_project):
    """Check if the box project is already initialized."""
    ut.check_boxproject()


def test_check_boxproject_error(rye_project_no_box):
    """Raise a click exception if the box project is not found."""
    with pytest.raises(ClickException):
        ut.check_boxproject()


def test_check_pyproject(rye_project):
    """Check if pyproject.toml file is found."""
    ut.check_pyproject()


def test_check_pyproject_error(tmp_path):
    """Raise a click exception if a pyproject.toml file is not found."""
    with ut.set_dir(tmp_path):
        with pytest.raises(ClickException):
            ut.check_pyproject()


def test_set_dir(tmp_path):
    """Change to a different folder inside context manager, then change back"""
    origin = Path.cwd()
    with ut.set_dir(tmp_path):
        assert tmp_path == Path.cwd()
    assert origin == Path.cwd()
