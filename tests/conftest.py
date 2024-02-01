# Fixtures for pytest

import os
from pathlib import Path
import subprocess

import pytest

from box.config import pyproject_writer


@pytest.fixture
def tmp_path_chdir(tmp_path):
    """Change directory to tmp_path and set back at end."""
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(Path().absolute())


@pytest.fixture
def rye_project(tmp_path):
    """Create a valid project for a minimum `rye` configured project."""
    # dump environment variables with subprocess
    subprocess.run("rye init .", cwd=tmp_path, shell=True, stdout=subprocess.DEVNULL)

    # add builder for box to pyproject.toml
    current_dir = Path().absolute()
    os.chdir(tmp_path)
    pyproject_writer("builder", "rye")

    yield tmp_path

    # clean up
    os.chdir(current_dir)
