# Test the pyproject parser

from pathlib import Path

import pytest

from box.config import PyProjectParser, pyproject_writer

TOML_BASIC_FILE = """[project]
name = "my-app"
version = "0.1.0"
"""


def test_pyproject_parser_file_not_found(tmp_path_chdir):
    """Test the pyproject parser for a missing `pyproject.toml` file."""
    with pytest.raises(FileNotFoundError):
        PyProjectParser()


def test_pyproject_parser_file_invalid(tmp_path_chdir):
    """Test the pyproject parser for an invalid `pyproject.toml` file."""
    tmp_path_chdir.joinpath("pyproject.toml").write_text("")
    with pytest.raises(KeyError) as err:
        PyProjectParser()

    assert "Not a valid pyproject.toml file" in err.value.args[0]


def test_pyproject_parser_basic_project(tmp_path_chdir):
    """Test the pyproject parser for a random project."""
    tmp_path_chdir.joinpath("pyproject.toml").write_text(TOML_BASIC_FILE)
    parser = PyProjectParser()
    assert parser.name == "my-app"
    assert parser.name_pkg == "my_app"
    assert parser.version == "0.1.0"


def test_pyproject_parser_entry_point(tmp_path_chdir):
    """Try to get an entry point for the app from project.scripts."""
    TOML_FILE = (
        TOML_BASIC_FILE
        + """

[project.scripts]
run = "my-app.app:run"

[project.gui-scripts]
run = "my-app.gui:run"
run2 = "my-app.gui:run2"
"""
    )

    possible_entries_exp = {
        "gui-scripts": {"run": "my-app.gui:run", "run2": "my-app.gui:run2"},
        "scripts": {"run": "my-app.app:run"},
    }

    tmp_path_chdir.joinpath("pyproject.toml").write_text(TOML_FILE)
    parser = PyProjectParser()
    assert parser.possible_app_entries == possible_entries_exp


def test_pyproject_parser_rye_project(rye_project):
    """Test the pyproject parser for a valid `rye` project."""
    parser = PyProjectParser()
    assert isinstance(parser.name, str)
    assert isinstance(parser.version, str)
    assert isinstance(parser.rye, dict)
    assert isinstance(parser.is_gui, bool)


def test_pyproject_writer_set_entry(tmp_path_chdir):
    """Set the app entry in the pyproject.toml file."""
    fname = "pyproject.toml"
    app_entry = "entry_point"

    tmp_path_chdir.joinpath(fname).write_text(TOML_BASIC_FILE)
    pyproject_writer("app_entry", "entry_point")
    parser = PyProjectParser()
    assert parser.app_entry == app_entry


def test_pyproject_writer_add_builder(tmp_path_chdir):
    """Test the pyproject writer for adding a builder."""
    fname = "pyproject.toml"

    tmp_path_chdir.joinpath(fname).write_text(TOML_BASIC_FILE)
    pyproject_writer("builder", "rye")
    parser = PyProjectParser()
    assert parser.builder == "rye"


def test_pyproject_writer_change_builder(tmp_path_chdir):
    """Test the pyproject writer for changing a builder."""
    fname = "pyproject.toml"
    tmp_path_chdir.joinpath(fname).write_text(TOML_BASIC_FILE)
    pyproject_writer("builder", "rye")
    pyproject_writer("builder", "hatch")
    parser = PyProjectParser()
    assert parser.builder == "hatch"


def test_pyproject_writer_called_with_newline(tmp_path_chdir, mocker):
    """Ensure newline is always '\n', even on Windows (otherwise issue with tomllib)."""
    fname = "pyproject.toml"
    tmp_path_chdir.joinpath(fname).write_text(TOML_BASIC_FILE)

    # mock open
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    pyproject_writer("builder", "rye")
    print(tmp_path_chdir.absolute())

    mock_open.assert_called_with(Path(fname), "w", newline="\n")


def test_pyproject_writer_no_pyproject_toml_file(tmp_path_chdir):
    """Raise FileNotFound error if no pyproject.toml file in folder."""
    with pytest.raises(FileNotFoundError):
        pyproject_writer("builder", "rye")
