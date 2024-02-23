# Test utility functions.

from pathlib import Path

import pytest

import box.utils as ut


@pytest.mark.parametrize(
    "os_python",
    [["nt", "py"], ["posix", "python"]],
)
def test_cmd_python(mocker, os_python):
    """Get python on mulitple operating systems."""
    # mock os.name
    mocker.patch("os.name", os_python[0])
    assert ut.cmd_python() == os_python[1]


def test_set_dir(tmp_path):
    """Change to a different folder inside context manager, then change back"""
    origin = Path.cwd()
    with ut.set_dir(tmp_path):
        assert tmp_path == Path.cwd()
    assert origin == Path.cwd()
