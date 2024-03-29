# Test initialization of a new project with CLI

from click.testing import CliRunner
import pytest

from box.cli import cli
from box.config import PyProjectParser
from box.packager import PackageApp
import box.utils as ut


@pytest.mark.parametrize(
    "app_entry",
    ["\n\n\nhello\n\n3.8\nPYAPP_FULL_ISOLATION 1", "\ngui\n\n127\nhello\nmodule\n\n"],
)
def test_initialize_project_app_entry_typed(rye_project_no_box, app_entry):
    """Initialize a new project."""
    # provided app_entry values
    app_entry_split = app_entry.split("\n")
    deps_exp = app_entry_split[0]
    app_entry_exp = app_entry_split[-4]
    entry_type_exp = app_entry_split[-3]
    py_version_exp = app_entry_split[-2]
    optional_pyapp_vars_exp = app_entry_split[-1]

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

    pyproj = PyProjectParser()

    # assert correct app_entry
    assert pyproj.app_entry == app_entry_exp

    # assert correct app_entry_type
    if entry_type_exp == "":
        entry_type_exp = "spec"  # default value
    assert pyproj.app_entry_type == entry_type_exp

    # assert that extra dependencies were set
    if deps_exp != "":
        assert pyproj.optional_dependencies == deps_exp

    # assert that default builder is set to rye
    assert pyproj.builder == "rye"

    # assert not a gui project
    assert not pyproj.is_gui

    # assert default python version
    if py_version_exp == "":
        py_version_exp = ut.PYAPP_PYTHON_VERSIONS[-1]
    assert pyproj.python_version == py_version_exp

    # optional pyapp variables
    if optional_pyapp_vars_exp == "":
        exp_dict = {}
    else:
        tmp_split = optional_pyapp_vars_exp.split()
        exp_dict = {}
        for it in range(0, len(tmp_split), 2):
            exp_dict[tmp_split[it]] = tmp_split[it + 1]
    assert pyproj.optional_pyapp_variables == exp_dict


@pytest.mark.parametrize("gui", [True, False])
def test_initialize_with_options(rye_project_no_box, gui):
    """Initialize a new project with options."""
    py_version = "3.8"
    entry_point = "myapp:entry"
    entry_type = "module"
    optional_deps = "gui"
    builder = "hatch"

    args = [
        "init",
        "-e",
        entry_point,
        "-et",
        entry_type,
        "-py",
        py_version,
        "-opt",
        optional_deps,
        "-b",
        builder,
        "--opt-pyapp-vars",
        "PYAPP_FULL_ISOLATION 1",
    ]
    if gui:
        args.append("--gui")

    runner = CliRunner()
    result = runner.invoke(cli, args)

    assert result.exit_code == 0
    assert "Project initialized." in result.output

    # assert it's now a box project
    pyproj = PyProjectParser()
    assert pyproj.is_box_project

    # assert settings in pyproject are according to options selected
    assert pyproj.builder == builder
    assert pyproj.python_version == py_version
    assert pyproj.optional_dependencies == optional_deps
    assert pyproj.is_gui == gui
    assert pyproj.app_entry == entry_point
    assert pyproj.app_entry_type == entry_type
    assert pyproj.optional_pyapp_variables == {"PYAPP_FULL_ISOLATION": "1"}


@pytest.mark.parametrize("pyapp_extra_vars", ["PYAPP_FULL_ISOLATION 1", None])
def test_initialize_project_again(rye_project_no_box, pyapp_extra_vars):
    """Initialization of a previous project sets defaults from previous config."""
    builder = "build"
    entry_point = "myapp:entry"
    entry_type = "module"
    optional_deps = "gui"
    py_version = "3.8"

    args = [
        "init",
        "-e",
        entry_point,
        "-et",
        entry_type,
        "-py",
        py_version,
        "-opt",
        optional_deps,
        "-b",
        builder,
        "--gui",
    ]
    if pyapp_extra_vars:
        args.append("--opt-pyapp-vars")
        args.append(pyapp_extra_vars)

    runner = CliRunner()
    runner.invoke(
        cli,
        args,
    )

    # now re-initialize with quiet and assure that the same options are set
    runner.invoke(cli, ["init", "-q"])

    pyproj = PyProjectParser()
    assert pyproj.builder == builder
    assert pyproj.python_version == py_version
    assert pyproj.optional_dependencies == optional_deps
    assert pyproj.is_gui
    assert pyproj.app_entry == entry_point
    assert pyproj.app_entry_type == entry_type


def test_initialize_project_quiet(rye_project_no_box):
    """Initialize a new project quietly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "-q"])
    assert result.exit_code == 0
    assert "Project initialized." not in result.output

    # assert it's now a box project
    pyproj = PyProjectParser()
    assert pyproj.is_box_project

    assert pyproj.python_version == ut.PYAPP_PYTHON_VERSIONS[-1]


@pytest.mark.parametrize("builder", PackageApp().builders)
def test_initialize_project_builders(rye_project_no_box, builder):
    """Initialize a new project with a specific builder."""
    runner = CliRunner()
    result = runner.invoke(cli, ["init"], input=f"{builder}\n\n\nsome_entry")
    assert result.exit_code == 0

    # assert that default builder is set to rye
    pyproj = PyProjectParser()
    assert pyproj.builder == builder


def test_initialize_project_wrong_number_of_pyapp_vars(rye_project_no_box):
    """Initialize a new project with a specific builder."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["init"],
        input="\n\n\nhello\n\n\nPYAPP_FULL_ISOLATION 1 2\nPYAPP_FULL_ISOLATION 1",
    )
    assert result.exit_code == 0

    pyproj = PyProjectParser()
    exp_dict = {"PYAPP_FULL_ISOLATION": "1"}
    assert pyproj.optional_pyapp_variables == exp_dict


def test_initialize_project_quiet_no_project_script(rye_project_no_box):
    """Initialize a new project quietly with app_entry as the package name."""
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "-q"])
    assert result.exit_code == 0
    assert "Project initialized." not in result.output

    # assert it's now a box project
    pyproj = PyProjectParser()
    assert pyproj.is_box_project


def test_pyproject_does_not_exist():
    """Abort if no `pyroject.toml` file is found."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init", "-q"])
        assert result.exit_code != 0
        assert "No pyproject.toml file found" in result.output


def test_pyproject_invalid_toml(tmp_path_chdir):
    """Abort if `pyproject.toml` is invalid."""
    tmp_path_chdir.joinpath("pyproject.toml").write_text("")
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "-q"])
    assert result.exit_code != 0
    assert "Invalid `pyproject.toml` file" in result.output
