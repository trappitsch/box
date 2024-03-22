"""Test initialization of a new project with the function.

Only functions that are not tested within the CLI are tested here.
"""

from box.config import PyProjectParser
from box.initialization import InitializeProject


def test_app_entry(rye_project_no_box):
    """Set the configuration in `pyproject.toml` to rye."""
    init = InitializeProject(quiet=True)
    init.initialize()

    pyproj = PyProjectParser()
    assert pyproj.app_entry == f"{rye_project_no_box.name}:run"


def test_set_builder(rye_project_no_box):
    """Set the configuration in `pyproject.toml` to rye."""
    init = InitializeProject(quiet=True)
    init.initialize()

    pyproj = PyProjectParser()

    assert pyproj.builder == "rye"
