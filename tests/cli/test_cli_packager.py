# Test builder with CLI - system calls mostly mocked, full build in unit tests

import os
import shutil
import sys
import urllib.request
from pathlib import Path

import pytest
from click.testing import CliRunner

from box.cli import cli


@pytest.mark.parametrize("verbose", [True, False])
def test_package_project(rye_project, mocker, verbose):
    """Package an initialized project, verbose and not."""
    # mock subprocess
    sp_devnull_mock = mocker.patch("subprocess.DEVNULL")
    sp_run_mock = mocker.patch("subprocess.run")

    # handle verbose mode
    subp_kwargs = {}
    if verbose:
        cmd = ["package", "-v"]
    else:
        cmd = ["package"]
        subp_kwargs["stdout"] = sp_devnull_mock
        subp_kwargs["stderr"] = sp_devnull_mock

    # mock urllib.request.urlretrieve
    mocker.patch.object(urllib.request, "urlretrieve")

    # mock tarfile.open
    mocker.patch("tarfile.open")

    # create dist folder and package
    dist_folder = rye_project.joinpath("dist")
    dist_folder.mkdir()
    dist_folder.joinpath(f"{rye_project.name.replace('-', '_')}-v0.1.0.tar.gz").touch()

    # create fake source and pyapp directory
    build_dir = rye_project.joinpath("build")
    pyapp_dir = build_dir.joinpath("pyapp-v1.2.3")
    pyapp_dir.mkdir(parents=True)
    build_dir.joinpath("pyapp-source.tar.gz").touch()

    # create fake binary
    cargo_target = build_dir.joinpath("pyapp-v1.2.3/target/release")
    cargo_target.mkdir(parents=True)
    exename = "pyapp.exe" if sys.platform == "win32" else "pyapp"
    cargo_target.joinpath(exename).touch()

    runner = CliRunner()
    result = runner.invoke(cli, cmd)
    assert result.exit_code == 0
    assert "Project successfully packaged." in result.output

    # assert system calls
    sp_run_mock.assert_any_call(
        ["rye", "build", "--out", f"{Path.cwd().joinpath('dist')}", "--sdist"],
        **subp_kwargs,
    )
    sp_run_mock.assert_called_with(
        ["cargo", "build", "--release"], cwd=pyapp_dir, **subp_kwargs
    )


@pytest.mark.parametrize("pyapp_source_name", ["pyapp-source.tar.gz", "pyapp-v0.14.0"])
def test_package_project_local_pyapp(rye_project, mocker, data_dir, pyapp_source_name):
    """Package an initialized project with local pyapp source."""
    mocker.patch("subprocess.run")
    urllib_mock = mocker.patch.object(urllib.request, "urlretrieve")  # not called

    mocker.patch("box.packager.PackageApp._package_pyapp")
    mocker.patch("box.packager.PackageApp.binary_name", return_value="pyapp")

    # create dist folder and package
    dist_folder = rye_project.joinpath("dist")
    dist_folder.mkdir()
    dist_folder.joinpath(f"{rye_project.name.replace('-', '_')}-v0.1.0.tar.gz").touch()

    runner = CliRunner()
    result = runner.invoke(cli, ["package", "-p", data_dir.joinpath(pyapp_source_name)])

    assert result.exit_code == 0
    urllib_mock.assert_not_called()

    assert rye_project.joinpath("build/pyapp-local/source.txt").is_file()


def test_package_project_do_not_copy_local_folder_twice(rye_project, data_dir, mocker):
    """Re-copying local folder echos a warning and does nothing."""
    pyapp_source_name = "pyapp-v0.14.0"

    mocker.patch("box.packager.PackageApp._package_pyapp")
    mocker.patch("box.packager.PackageApp.binary_name", return_value="pyapp")
    urllib_mock = mocker.patch.object(urllib.request, "urlretrieve")

    # create dist folder and package
    dist_folder = rye_project.joinpath("dist")
    dist_folder.mkdir()
    dist_folder.joinpath(f"{rye_project.name.replace('-', '_')}-v0.1.0.tar.gz").touch()

    runner = CliRunner()
    result = runner.invoke(cli, ["package", "-p", data_dir.joinpath(pyapp_source_name)])

    assert result.exit_code == 0
    assert rye_project.joinpath("build/pyapp-local/source.txt").is_file()

    result2 = runner.invoke(
        cli, ["package", "-p", data_dir.joinpath(pyapp_source_name)]
    )

    assert "Local source folder already copied." in result2.output

    urllib_mock.assert_not_called()


@pytest.mark.parametrize("pyapp_version", ["v0.14.0", "latest"])
def test_package_with_specific_pyapp_version(
    rye_project, data_dir, mocker, pyapp_version
):
    """Get a specific pyapp version for packaging."""
    # source and destination for side_effect copy call
    pyapp_src = data_dir.joinpath("pyapp-source.tar.gz").absolute()
    pyapp_dest_folder = rye_project.joinpath("build")
    pyapp_dest_folder.mkdir()
    pyapp_dest = pyapp_dest_folder.joinpath("pyapp-source.tar.gz")

    mocker.patch("subprocess.run")
    mocker.patch("box.packager.PackageApp._package_pyapp")
    mocker.patch("box.packager.PackageApp.binary_name", return_value="pyapp")
    urllib_retrieve_mock = mocker.patch.object(urllib.request, "urlretrieve")
    urllib_retrieve_mock.side_effect = lambda _1, _2: shutil.copy(pyapp_src, pyapp_dest)

    if pyapp_version == "latest":
        pyapp_url = (
            "https://github.com/ofek/pyapp/releases/latest/download/source.tar.gz"
        )
    else:
        pyapp_url = f"https://github.com/ofek/pyapp/releases/download/{pyapp_version}/source.tar.gz"
    pyapp_tar = Path("pyapp-source.tar.gz")

    Path.cwd().joinpath("build/pyapp-0.16.0").mkdir(parents=True)

    # create dist folder and package
    dist_folder = rye_project.joinpath("dist")
    dist_folder.mkdir()
    dist_folder.joinpath(f"{rye_project.name.replace('-', '_')}-v0.1.0.tar.gz").touch()

    runner = CliRunner()
    result = runner.invoke(cli, ["package", "-pv", pyapp_version])

    assert result.exit_code == 0

    urllib_retrieve_mock.assert_called_with(pyapp_url, pyapp_tar)


def test_cargo_not_found(rye_project, mocker):
    """Test that cargo not found raises an exception."""
    # mock $PATH to remove cargo
    mocker.patch.dict(os.environ, {"PATH": ""})

    runner = CliRunner()
    result = runner.invoke(cli, "package")

    assert result.exit_code == 1
    assert "cargo not found" in result.output
