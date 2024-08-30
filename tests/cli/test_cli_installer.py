### CLI tests for the installer

import os
import stat
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import rich_click as click
from click.testing import CliRunner

from box import config
from box.cli import cli


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


def setup_mock_icon(path: Path, suffix=None) -> str:
    """Set up a mock icon in the assets folder of the given path.

    :param path: The path to the project.
    :param ico: Whether to create an .ico file or not. Default not -> svg file.

    :return: The content of the icon file.
    """
    assets_dir = path.joinpath("assets")
    assets_dir.mkdir(parents=True)
    icon_file = assets_dir.joinpath(f"icon{suffix}" if suffix else "icon.svg")
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

    # assure we only have one `rm -rf` in the install file (for pyapp folder)
    assert file_content.count("rm -rf") == 1

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
    _ = setup_mock_icon(rye_project, suffix=".ico")
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


@pytest.mark.parametrize("verbose", [True, False])
def test_installer_cli_macos(rye_project, mocker, verbose):
    """Create an installer for macos using applecrate."""
    applecrate_mock = MagicMock()

    with patch.dict("sys.modules", {"applecrate": applecrate_mock}):
        mocker.patch("sys.platform", "darwin")
        conf = config.PyProjectParser()
        installer_fname_exp = f"{conf.name}-v0.1.0-macos.pkg"
        _ = setup_mock_target_binary(rye_project, conf.name)
        # create the installer binary
        installer_binary = rye_project.joinpath(f"target/release/{installer_fname_exp}")
        installer_binary.touch()

        call_args_exp = {
            "app": conf.name,
            "version": conf.version,
            "install": [
                (
                    Path("target/release").joinpath(conf.name),
                    f"/usr/local/bin/{conf.name}",
                ),
            ],
            "output": installer_binary.relative_to(rye_project),
        }

        # run the CLI
        args = ["installer"]
        if verbose:
            args.append("-v")
            call_args_exp["verbose"] = click.secho
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert result.exit_code == 0

        applecrate_mock.build_installer.assert_called_with(**call_args_exp)
        assert installer_fname_exp in result.output


def test_installer_gui_macos(rye_project, mocker):
    """Create an GUI installer dmg for macos."""
    dmgbuild_mock = MagicMock()

    with patch.dict("sys.modules", {"dmgbuild": dmgbuild_mock}):
        mocker.patch("sys.platform", "darwin")

        conf = config.PyProjectParser()
        installer_fname_exp = f"{conf.name}-v0.1.0-macos.dmg"

        _ = setup_mock_target_binary(rye_project, conf.name)
        _ = setup_mock_icon(rye_project, suffix=".icns")

        # create the installer binary
        installer_binary = rye_project.joinpath(f"target/release/{installer_fname_exp}")
        installer_binary.touch()

        # create app_file - must be deleted when starting the CLI
        app_file = rye_project.joinpath(f"target/release/{conf.name}").with_suffix(
            ".app"
        )
        app_file.mkdir()

        # make it a GUI project
        config.pyproject_writer("is_gui", True)

        hlp_settings_exp = {
            "files": [
                f"{rye_project.joinpath('target/release').joinpath(conf.name).with_suffix('.app').absolute()}"
            ],
            "symlinks": {"Applications": "/Applications"},
            "icon_locations": {
                f"{conf.name}.app": (140, 120),
                "Applications": (500, 120),
            },
            "background": "builtin-arrow",
        }
        call_args_exp = {
            "filename": installer_binary.with_suffix("").name,
            "volume_name": installer_fname_exp,
            "settings": hlp_settings_exp,
        }

        # run the CLI
        runner = CliRunner()
        result = runner.invoke(cli, ["installer"])

        assert result.exit_code == 0

        # assert there's no app file around at the end
        assert not app_file.exists()

        # dmg build assertions
        dmgbuild_mock.build_dmg.assert_called_with(**call_args_exp)
        assert installer_fname_exp in result.output


def test_not_implemented_installers(rye_project, mocker):
    """Present a warning but exit gracefully when installer is not implemented."""
    platform = "aix"
    # mock the platform to return with sys.platform
    mocker.patch("sys.platform", platform)

    conf = config.PyProjectParser()
    _ = setup_mock_target_binary(rye_project, conf.name)

    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    assert result.exit_code == 0
    assert "currently not supported" in result.output
    assert platform in result.output
