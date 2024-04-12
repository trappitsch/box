### CLI tests for the installer

import os
import sys
from pathlib import Path
import stat

from click.testing import CliRunner
import pytest

from box.cli import cli
from box import config


def setup_mock_target_binary(path: Path, release_name: str) -> str:
    """Set up a mock binary in the target/release folder of the given path.

    :param path: The path to the project.
    :param release_name: The name of the release.
    """
    target_dir = path.joinpath("target/release")
    target_dir.mkdir(parents=True)
    target_file = target_dir.joinpath(release_name)
    if sys.platform == "win32":
        target_file = target_file.with_suffix(".exe")
    target_file_content = "This is the content of the mock binary file..."
    target_file.write_text(target_file_content)
    return target_file_content


def setup_mock_icon(path: Path, ico=False) -> str:
    """Set up a mock icon in the assets folder of the given path.

    :param path: The path to the project.
    :param ico: Whether to create an .ico file or not. Default not -> svg file.

    :return: The content of the icon file.
    """
    assets_dir = path.joinpath("assets")
    assets_dir.mkdir(parents=True)
    icon_file = assets_dir.joinpath("icon.ico" if ico else "icon.svg")
    icon_file_content = "This is the content of the mock icon file..."
    icon_file.write_text(icon_file_content)
    return icon_file_content


@pytest.mark.parametrize("platform", ["linux", "darwin", "win32"])
def test_installer_no_binary(rye_project, platform, mocker):
    """Raise ClickException if no binary was found."""
    mocker.patch("sys.platform", platform)

    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    assert result.exit_code != 0
    assert result.exception
    assert "No release found." in result.output


@pytest.mark.skipif("sys.platform == 'win32'", reason="Not supported on Windows")
def test_installer_cli_linux(rye_project):
    """Create installer for linux CLI."""
    conf = config.PyProjectParser()
    installer_fname_exp = f"{conf.name}-v0.1.0-linux.sh"
    target_file_content = setup_mock_target_binary(rye_project, conf.name)

    # run the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    # assert result.exit_code == 0

    # assert the installer file was created
    installer_file = rye_project.joinpath(f"target/release/{installer_fname_exp}")
    assert installer_file.name in result.output

    assert installer_file.exists()
    assert target_file_content in installer_file.read_text()
    assert os.stat(installer_file).st_mode & stat.S_IXUSR != 0


@pytest.mark.skipif("sys.platform == 'win32'", reason="Not supported on Windows")
def test_installer_gui_linux(rye_project):
    """Create installer for linux GUI."""
    conf = config.PyProjectParser()
    installer_fname_exp = f"{conf.name}-v0.1.0-linux.sh"
    target_file_content = setup_mock_target_binary(rye_project, conf.name)
    icon_file_content = setup_mock_icon(rye_project)

    # make it a GUI project
    config.pyproject_writer("is_gui", True)

    # run the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    assert result.exit_code == 0

    # assert the installer file was created
    installer_file = rye_project.joinpath(f"target/release/{installer_fname_exp}")
    assert installer_file.exists()

    with open(installer_file, "rb") as f:
        file_content = f.read().decode("utf-8")

    start_successful_exec = file_content.find(
        'echo "Successfully installed $INSTALL_NAME to $INSTALL_DIR"'
    )
    binary_start = file_content.find("#__PROGRAM_BINARY__", start_successful_exec)
    icon_start = file_content.find("#__ICON_BINARY__", start_successful_exec)
    assert file_content.find(target_file_content, binary_start, icon_start) != -1
    assert file_content.find(icon_file_content, icon_start) != -1
    assert os.stat(installer_file).st_mode & stat.S_IXUSR != 0

    assert installer_file.name in result.output


@pytest.mark.parametrize("verbose", [True, False])
def test_installer_cli_windows(rye_project, mocker, verbose):
    """Create an installer with NSIS for a CLI on Windows."""
    mocker.patch("sys.platform", "win32")
    subp_mock = mocker.patch("subprocess.run")
    sp_devnull_mock = mocker.patch("subprocess.DEVNULL")

    subp_kwargs = {}
    if not verbose:
        subp_kwargs["stdout"] = subp_kwargs["stderr"] = sp_devnull_mock

    conf = config.PyProjectParser()
    installer_fname_exp = f"{conf.name}-v0.1.0-win.exe"
    _ = setup_mock_target_binary(rye_project, conf.name)
    # create the installer binary
    installer_binary = rye_project.joinpath(f"target/release/{installer_fname_exp}")
    installer_binary.touch()

    # run the CLI
    runner = CliRunner()
    if verbose:
        args = ["installer", "-v"]
    else:
        args = ["installer"]
    result = runner.invoke(cli, args)

    assert result.exit_code == 0

    make_installer_pth = rye_project.joinpath("target/release/make_installer.nsi")
    release_path = rye_project.joinpath("target/release")
    subp_mock.assert_called_with(
        ["makensis", make_installer_pth.relative_to(release_path)], **subp_kwargs
    )
    assert installer_fname_exp in result.output


def test_installer_cli_windows_not_created(rye_project, mocker):
    """Raise ClickException if the installer was not created."""
    mocker.patch("sys.platform", "win32")
    mocker.patch("subprocess.run")

    conf = config.PyProjectParser()
    _ = setup_mock_target_binary(rye_project, conf.name)

    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    assert result.exit_code != 0
    assert result.exception
    assert "Installer was not created" in result.output


@pytest.mark.parametrize("verbose", [True, False])
def test_installer_gui_windows(rye_project, mocker, verbose):
    """Create an installer with NSIS on Windows."""
    mocker.patch("sys.platform", "win32")
    subp_mock = mocker.patch("subprocess.run")
    sp_devnull_mock = mocker.patch("subprocess.DEVNULL")

    subp_kwargs = {}
    if not verbose:
        subp_kwargs["stdout"] = subp_kwargs["stderr"] = sp_devnull_mock

    conf = config.PyProjectParser()
    installer_fname_exp = f"{conf.name}-v0.1.0-win.exe"
    _ = setup_mock_target_binary(rye_project, conf.name)
    _ = setup_mock_icon(rye_project, ico=True)
    # create the installer binary
    installer_binary = rye_project.joinpath(f"target/release/{installer_fname_exp}")
    installer_binary.touch()

    # make it a GUI project
    config.pyproject_writer("is_gui", True)

    # run the CLI
    runner = CliRunner()
    if verbose:
        args = ["installer", "-v"]
    else:
        args = ["installer"]
    result = runner.invoke(cli, args)

    assert result.exit_code == 0

    make_installer_pth = rye_project.joinpath("target/release/make_installer.nsi")
    release_path = rye_project.joinpath("target/release")
    subp_mock.assert_called_with(
        ["makensis", make_installer_pth.relative_to(release_path)], **subp_kwargs
    )
    assert installer_fname_exp in result.output


@pytest.mark.parametrize("platform", ["darwin", "aix"])
def test_not_implemented_installers(rye_project, mocker, platform):
    """Present a warning but exit gracefully when installer is not implemented."""
    # mock the platform to return with sys.platform
    mocker.patch("sys.platform", platform)

    os_exp = ""
    if platform == "darwin":
        os_exp = "macOS"

    conf = config.PyProjectParser()
    _ = setup_mock_target_binary(rye_project, conf.name)

    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    assert result.exit_code == 0
    assert "currently not supported" in result.output
    assert os_exp in result.output
