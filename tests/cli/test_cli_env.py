# Tests for setting environment variables with `box env ...`

import pytest
from click.testing import CliRunner

from box.cli import cli


def test_env_not_box_project(rye_project_no_box):
    """Ensure we check first if this is a box project."""
    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set", "MY_VAR=3"])

    assert result.exit_code != 0
    assert "not a box project" in result.output


@pytest.mark.parametrize("my_vars", [["PYAPP_SOMETHING", 1], ["TEST_ENV", "qerty"]])
def test_env_set(rye_project, my_vars):
    """Set some environments in the box project and ensure they are there."""
    var = my_vars[0]
    value = my_vars[1]

    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set", f"{var}={value}"])

    assert result.exit_code == 0

    with open("pyproject.toml") as fl:
        data = fl.read()
    assert "[tool.box.env-vars]" in data
    assert f'{var} = "{value}"' in data

    assert var in result.output
    assert f"{value}" in result.output
    assert "type string" in result.output


@pytest.mark.parametrize("key_val", ["key=value=something", "only_a_key"])
def test_env_set_key_value_invalid(rye_project, key_val):
    """Ensure an error is raised if key-value pair to be set is invalid."""
    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set", key_val])

    assert result.exit_code != 0
    assert "Variables to set must be a key-value pair" in result.output


def test_env_set_int(rye_project):
    """Set an integer environments in the box project and ensure they it's there."""
    var = "MY_VARIABLE"
    value = 42

    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set-int", f"{var}={value}"])

    assert result.exit_code == 0

    with open("pyproject.toml") as fl:
        data = fl.read()
    assert "[tool.box.env-vars]" in data
    assert f"{var} = {value}" in data

    assert var in result.output
    assert f" {value} " in result.output
    assert "type int" in result.output


def test_env_set_int_convertion_error(rye_project):
    """Raise conversion error if int variable setting with invalid value."""
    var = "MY_VARIABLE"
    value = "b3sdf"

    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set-int", f"{var}={value}"])

    assert result.exit_code != 0
    assert "Problem converting" in result.output
    assert value in result.output


@pytest.mark.parametrize(
    "value_bool",
    [
        ["0", False],
        ["1", True],
        ["False", False],
        ["True", True],
        ["falSE", False],
        ["true", True],
    ],
)
def test_env_set_bool(rye_project, value_bool):
    """Set some bool environments in the box project and ensure they are there."""
    var = "MY_VARIABLE"
    value, vbool = value_bool

    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set-bool", f"{var}={value}"])

    assert result.exit_code == 0

    with open("pyproject.toml") as fl:
        data = fl.read()
    assert "[tool.box.env-vars]" in data
    assert f"{var} = {str(vbool).lower()}" in data

    assert var in result.output
    assert f"{vbool}" in result.output
    assert "type bool" in result.output


def test_env_set_bool_convertion_error(rye_project):
    """Raise conversion error if bool variable setting with invalid bool."""
    var = "MY_VARIABLE"
    value = "b3sdf a"

    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set-bool", f"{var}={value}"])

    assert result.exit_code != 0
    assert "Cannot convert" in result.output
    assert value in result.output


def test_env_get(rye_project):
    """First set, then get an environment variable from box project."""
    var = "MY_VARIABLE"
    value = "42"

    runner = CliRunner()
    runner.invoke(cli, ["env", "--set-int", f"{var}={value}"])
    result = runner.invoke(cli, ["env", "--get", var])

    assert result.exit_code == 0
    assert value in result.output
    assert var not in result.output


def test_env_list(rye_project):
    """List all environment variables set in the box project."""
    my_vars = [["PYAPP_SOMETHING", 1], ["TEST_ENV", "qerty"]]

    runner = CliRunner()

    result_none = runner.invoke(cli, ["env", "--list"])

    for var, value in my_vars:
        runner.invoke(cli, ["env", "--set", f"{var}={value}"])
    result_some = runner.invoke(cli, ["env", "--list"])

    assert result_none.exit_code == 0
    assert "No variables set" in result_none.output

    assert result_some.exit_code == 0
    for var, value in my_vars:
        assert var in result_some.output
        assert f"{value}" in result_some.output


def test_env_get_na(rye_project):
    """If no variable with given name is present, print a warning."""
    runner = CliRunner()
    result = runner.invoke(cli, "env --get SOME_VARIABLE")

    assert result.exit_code == 0
    assert "Warning:" in result.output


def test_env_unset(rye_project):
    """Unset an already set variable."""
    var = "MY_VAR"
    val = 42

    runner = CliRunner()

    runner.invoke(cli, ["env", "--set-int", f"{var}={val}"])
    result_1 = runner.invoke(cli, ["env", "--get", var])
    runner.invoke(cli, ["env", "--unset", var])
    result_2 = runner.invoke(cli, ["env", "--get", var])

    result_3 = runner.invoke(cli, ["env", "--unset", var])

    assert "Warning" not in result_1.output
    assert "Warning" in result_2.output

    assert "Warning" in result_3.output
