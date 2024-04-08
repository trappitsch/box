### CLI tests for the installer

from pathlib import Path

from click.testing import CliRunner

from box.cli import cli


def setup_mock_target_binary(path: Path) -> str:
    """Set up a mock binary in the target/release folder of the given path."""
    target_dir = path.joinpath("target/release")
    target_dir.mkdir(parents=True)
    target_file = target_dir.joinpath("binary")
    target_file_content = "This is the content of the mock binary file..."
    target_file.write_text(target_file_content)
    return target_file_content


def test_installer_cli_linux(rye_project, mocker):
    """Test the installer CLI on a Linux system."""
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
