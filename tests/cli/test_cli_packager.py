# Test builder with CLI - system calls mostly mocked, full build in unit tests


from click.testing import CliRunner

from box.cli import cli


def test_initialize_project(rye_project, mocker):
    """Initialize a new project."""
    # mock subprocess.run
    sp_devnull_mock = mocker.patch("subprocess.DEVNULL")
    sp_run_mock = mocker.patch("subprocess.run")

    runner = CliRunner()
    result = runner.invoke(cli, ["package"])
    assert result.exit_code == 0
    assert result.output.__contains__("Project successfully packaged.")

    sp_run_mock.assert_called_with(["rye", "build"], stdout=sp_devnull_mock)
