# Tests for setting environment variables with `box env ...`

from click.testing import CliRunner
import pytest

from box.cli import cli


def test_env_not_box_project(rye_project_no_box):
    """Ensure we check first if this is a box project."""
    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set", "MY_VAR=3"])

    assert result.exit_code != 0
    assert "not a box project" in result.output


@pytest.mark.parametrize("vars", [["PYAPP_SOMETHING", 1], ["TEST_ENV", "qerty"]])
def test_env_set(rye_project, vars):
    """Set some environments in the box project and ensure they are there."""
    var = vars[0]
    value = vars[1]

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
    """Set some environments in the box project and ensure they are there."""
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
    """Set some environments in the box project and ensure they are there."""
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
    """Set some environments in the box project and ensure they are there."""
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
    """Set some environments in the box project and ensure they are there."""
    var = "MY_VARIABLE"
    value = "b3sdf a"

    runner = CliRunner()
    result = runner.invoke(cli, ["env", "--set-bool", f"{var}={value}"])

    assert result.exit_code != 0
    assert "Cannot convert" in result.output
    assert value in result.output