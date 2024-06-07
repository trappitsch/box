"""Unit tests for the installer module."""

import os
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


def test_create_installer_check_makensis(rye_project, mocker):
    """Create an installer file."""
    mocker.patch.dict(os.environ, {"PATH": ""})

    cri = inst.CreateInstaller()

    with pytest.raises(click.ClickException) as e:
        cri._check_makensis()

    assert "NSIS is not installed or not available on the PATH." in str(e.value)


@pytest.mark.parametrize("suffix", ["svg", "png", "jpg", "jpeg"])
def test_get_icon(suffix, tmp_path_chdir):
    """Get an icon file for various suffixes."""
    create_icon(suffix, Path.cwd())

    assert isinstance(inst.get_icon(), Path)


@pytest.mark.parametrize("suffix", ["svg", "png", "jpg", "jpeg"])
def test_get_icon_subfolder(suffix, tmp_path_chdir):
    """Get an icon file for various suffixes from src/package/assets folder."""
    fldr = Path.cwd().joinpath("src").joinpath("package")
    fldr.mkdir(parents=True)
    create_icon(suffix, fldr)

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


def test_get_icon_no_icon_in_subfolders(tmp_path_chdir):
    """Raise an exception if no icon file is found and skip excluded folders."""
    # put some icons into folders that must be excluded
    dist = Path.cwd().joinpath("dist")
    dist.mkdir()
    create_icon("svg", dist)
    build = Path.cwd().joinpath("build")
    build.mkdir()
    create_icon("svg", build)
    target = Path.cwd().joinpath("target")
    target.mkdir()
    create_icon("svg", target)
    venv = Path.cwd().joinpath("venv")
    venv.mkdir()
    create_icon("svg", venv)
    hidden_src = Path.cwd().joinpath(".src")
    hidden_src.mkdir()
    create_icon("svg", hidden_src)

    with pytest.raises(click.ClickException):
        inst.get_icon()


def test_get_icon_icon_in_wrong_folder(tmp_path_chdir):
    """Raise an exception icon file cannot be found in assets folder."""
    # put some icons into folders that must be excluded
    fldr = Path.cwd().joinpath("src")
    fldr.mkdir()
    create_icon("ico", fldr)

    with pytest.raises(click.ClickException):
        inst.get_icon()
