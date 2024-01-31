# Test utility functions.

from pathlib import Path

import box.utils as ut


def test_set_dir(tmp_path):
    """Change to a different folder inside context manager, then change back"""
    origin = Path.cwd()
    with ut.set_dir(tmp_path):
        assert tmp_path == Path.cwd()
    assert origin == Path.cwd()
