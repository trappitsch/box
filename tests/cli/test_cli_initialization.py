# Test initialization of a new project with CLI

from click.testing import CliRunner

from box.cli import cli, init
from box.config import PyProjectParser


def test_initialize_project(rye_project_no_box):
    """Initialize a new project."""
    runner = CliRunner()
    result = runner.invoke(cli, ["init"])

    # accept default config for name config
    name_result = runner.invoke(init, input="")
    assert not name_result.exception

    # proper app exit
    assert result.exit_code == 0
    assert "Project initialized." in result.output

    # assert name is in pyproject.toml
    pyproj = PyProjectParser()
    # todo: assert name is in pyproject.toml under [tool.box]
    # todo: add a test where we modify the name
    # todo: continue with further queries
    # assert pyproj.name ==


def test_initialize_project_quiet(rye_project_no_box):
    """Initialize a new project."""
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "-q"])
    assert result.exit_code == 0
    assert "Project initialized." not in result.output

    # assert it's now a box project
    pyproj = PyProjectParser()
    assert pyproj.is_box_project


# EXCEPTIONS #


def test_no_builder():
    """Abort if no builder tooling was found."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write toml file with no builder
        with open("pyproject.toml", "w") as f:
            f.write(
                """[project]
name = "myapp"
version = "0.1.0"
"""
            )

        result = runner.invoke(cli, ["init", "-q"])
        assert result.exit_code != 0
        assert result.output.__contains__("No builder tool was found in configuration.")


def test_pyproject_does_not_exist():
    """Abort if no `pyroject.toml` file is found."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init", "-q"])
        assert result.exit_code != 0
        assert result.output.__contains__("No `pyproject.toml` file found")


def test_pyproject_invalid_toml(tmp_path_chdir):
    """Abort if `pyproject.toml` is invalid."""
    tmp_path_chdir.joinpath("pyproject.toml").write_text("")
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "-q"])
    assert result.exit_code != 0
    assert result.output.__contains__("Invalid `pyproject.toml` file")
