### CLI tests for the installer

import os
from pathlib import Path
import stat

from click.testing import CliRunner
import pytest

from box.cli import cli


def setup_mock_target_binary(path: Path) -> str:
    """Set up a mock binary in the target/release folder of the given path."""
    target_dir = path.joinpath("target/release")
    target_dir.mkdir(parents=True)
    target_file = target_dir.joinpath(path.name)
    target_file_content = "This is the content of the mock binary file..."
    target_file.write_text(target_file_content)
    return target_file_content


def test_installer_no_binary(rye_project):
    """Raise ClickException if no binary was found."""
    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    assert result.exit_code != 0
    assert result.exception
    assert "No release found." in result.output


def test_installer_cli_linux(rye_project):
    """Create installer for linux CLI."""
    installer_fname_exp = f"{rye_project.name}-v0.1.0-linux.sh"
    target_file_content = setup_mock_target_binary(rye_project)

    # run the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    assert result.exit_code == 0

    # assert the installer file was created
    installer_file = rye_project.joinpath(f"target/release/{installer_fname_exp}")
    assert installer_file.exists()
    assert target_file_content in installer_file.read_text()
    assert os.stat(installer_file).st_mode & stat.S_IXUSR != 0


@pytest.mark.parametrize("platform", ["win32", "darwin", "aix"])
def test_not_implemented_installers(rye_project, mocker, platform):
    """Present a warning but exit gracefully when installer is not implemented."""
    # mock the platform to return with sys.platform
    mocker.patch("sys.platform", platform)

    os_exp = ""
    if platform == "win32":
        os_exp = "Windows"
    elif platform == "darwin":
        os_exp = "macOS"

    _ = setup_mock_target_binary(rye_project)

    runner = CliRunner()
    result = runner.invoke(cli, ["installer"])

    assert result.exit_code == 0
    assert "currently not supported" in result.output
    assert os_exp in result.output
