"""Test initialization of a new project with the function.

Only functions that are not tested within the CLI are tested here.
"""

from box.config import PyProjectParser
from box.initialization import InitializeProject


def test_quiet_init(rye_project_no_box):
    """Check default configuration upon a quiet init."""
    init = InitializeProject(quiet=True)
    init.initialize()

    pyproj = PyProjectParser()

    assert pyproj.builder == "rye"
    assert pyproj.optional_dependencies is None
    assert not pyproj.is_gui
    assert pyproj.app_entry == f"{rye_project_no_box.name}:run"
    assert pyproj.app_entry_type == "spec"
    assert pyproj.python_version == "3.12"
    assert pyproj.optional_pyapp_variables == {}
