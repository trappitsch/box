"""Tests for un-initializing a project."""

from click.testing import CliRunner

from box.cli import cli
from box.config import PyProjectParser


def test_uninitialize(rye_project):
    """Assure project is not a box project after un-initialization."""
    runner = CliRunner()
    result = runner.invoke(cli, ["uninit"])

    assert result.exit_code == 0
    assert "Project un-initialized." in result.output

    # assert it's not a box project
    pyproj = PyProjectParser()
    assert not pyproj.is_box_project


def test_uninitialize_clean(rye_project, mocker):
    """Assure a full clean is called if option `-c` is given."""
    clean_mock = mocker.patch("box.cli.clean")

    runner = CliRunner()
    result = runner.invoke(cli, ["uninit", "-c"])

    assert result.exit_code == 0
    assert "Project un-initialized." in result.output

    # assert it's not a box project
    pyproj = PyProjectParser()
    assert not pyproj.is_box_project

    # assert clean was called
    clean_mock.assert_called_once()
