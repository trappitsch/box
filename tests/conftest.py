# Fixtures for pytest

import os
from pathlib import Path
import subprocess

import pytest

from box.config import pyproject_writer


@pytest.fixture
def data_dir():
    """Return the path to the data directory."""
    return Path(__file__).parent.joinpath("data")


@pytest.fixture
def min_proj_no_box(tmp_path):
    """Create a minimal project with a `pyproject.toml` file."""
    current_dir = Path().absolute()
    os.chdir(tmp_path)
    toml_data = """[project]
name = "myapp"
version = "0.1.0"
dependencies = []
"""
    with open("pyproject.toml", "w") as f:
        f.write(toml_data)

    yield tmp_path

    # clean up
    os.chdir(current_dir)


@pytest.fixture
def tmp_path_chdir(tmp_path):
    """Change directory to tmp_path and set back at end."""
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(Path().absolute())


@pytest.fixture
def rye_project(tmp_path):
    """Create a valid project for a minimum `rye` configured project with box."""
    # dump environment variables with subprocess
    subprocess.run("rye init .", cwd=tmp_path, shell=True, stdout=subprocess.DEVNULL)

    # add builder for box to pyproject.toml
    current_dir = Path().absolute()
    os.chdir(tmp_path)
    pyproject_writer("builder", "rye")
    pyproject_writer("app_entry", "pkg:run")
    pyproject_writer("entry_type", "spec")
    pyproject_writer("is_gui", False)
    pyproject_writer("python_version", "3.12")

    yield tmp_path

    # clean up
    os.chdir(current_dir)


@pytest.fixture
def rye_project_no_box(tmp_path):
    """Create a valid project for a minimum `rye` configured project."""
    # dump environment variables with subprocess
    subprocess.run("rye init .", cwd=tmp_path, shell=True, stdout=subprocess.DEVNULL)

    # add builder for box to pyproject.toml
    current_dir = Path().absolute()
    os.chdir(tmp_path)

    yield tmp_path

    # clean up
    os.chdir(current_dir)
