# Test initialization of a new project with CLI

from click.testing import CliRunner
import pytest

from box.cli import cli
from box.config import PyProjectParser


@pytest.mark.parametrize("app_entry", ["\nhello", "gui\n127\nhello"])
def test_initialize_project_app_entry_typed(rye_project_no_box, app_entry):
    """Initialize a new project."""
    # modify pyproject.toml to contain an app entry
    with open("pyproject.toml") as fin:
        toml_data = fin.read().split("\n")
    idx = toml_data.index("[build-system]")
    toml_data.insert(idx, "[project.scripts]")
    toml_data.insert(idx + 1, "run = 'something'\n")
    with open("pyproject.toml", "w") as fout:
        fout.write("\n".join(toml_data))

    runner = CliRunner()
    result = runner.invoke(cli, ["init"], input=app_entry)

    # accept default config for name config
    assert not result.exception

    # proper app exit
    assert result.exit_code == 0
    assert "Project initialized." in result.output

    # assert name is in pyproject.toml
    pyproj = PyProjectParser()
    app_entry_exp = app_entry.split("\n")[-1]
    assert pyproj.app_entry == app_entry_exp

    # assert that extra dependencies were set
    if (deps_exp := app_entry.split("\n")[0]) != "":
        assert pyproj.optional_dependencies == deps_exp


def test_initialize_project_quiet(rye_project_no_box):
    """Initialize a new project quietly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "-q"])
    assert result.exit_code == 0
    assert "Project initialized." not in result.output

    # assert it's now a box project
    pyproj = PyProjectParser()
    assert pyproj.is_box_project


def test_initialize_project_quiet_no_project_script(rye_project_no_box):
    """Initialize a new project quietly with app_entry as the package name."""
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
