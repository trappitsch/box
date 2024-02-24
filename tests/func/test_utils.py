# Test utility functions.

from pathlib import Path

import pytest
from rich_click import ClickException

import box.utils as ut


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
