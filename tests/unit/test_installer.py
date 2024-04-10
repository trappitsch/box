"""Unit tests for the installer module."""

from pathlib import Path

import pytest
import rich_click as click

from box import installer as inst


def create_icon(suffix: str, path: Path) -> None:
    """Create an icon file in assets folder of current path.

    :param suffix: The suffix of the icon file.
    :param path: The path to the current folder.
    """
    assets = path.joinpath("assets")
    assets.mkdir()
    icon_file = assets.joinpath(f"icon.{suffix}")
    icon_file.touch()


@pytest.mark.parametrize("suffix", ["svg", "png", "jpg", "jpeg"])
def test_get_icon(suffix, tmp_path_chdir):
    """Get an icon file for various suffixes."""
    create_icon(suffix, Path.cwd())

    assert isinstance(inst.get_icon(), Path)


def test_get_specific_icon(tmp_path_chdir):
    """Get an `.ico` file back from the get_icon routine."""
    create_icon("ico", Path.cwd())

    result = inst.get_icon("ico")
    assert result.suffix == ".ico"
    assert isinstance(result, Path)


def test_get_icon_no_icon(tmp_path_chdir):
    """Raise an exception if no icon file is found."""
    with pytest.raises(click.ClickException):
        inst.get_icon()
