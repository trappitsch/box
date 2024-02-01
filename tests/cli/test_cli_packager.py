# Test builder with CLI - system calls mostly mocked, full build in unit tests

import urllib.request

from click.testing import CliRunner

from box.cli import cli


def test_initialize_project(rye_project, mocker):
    """Initialize a new project."""
    # mock subprocess
    sp_devnull_mock = mocker.patch("subprocess.DEVNULL")
    sp_run_mock = mocker.patch("subprocess.run")

    # mock urllib.request.urlretrieve
    mocker.patch.object(urllib.request, "urlretrieve")

    # mock tarfile.open
    mocker.patch("tarfile.open")

    # create dist folder and package
    dist_folder = rye_project.joinpath("dist")
    dist_folder.mkdir()
    dist_folder.joinpath(f"{rye_project.name.replace("-", "_")}-v0.1.0.tar.gz").touch()

    # create fake source and pyapp directory
    build_dir = rye_project.joinpath("build")
    pyapp_dir = build_dir.joinpath("pyapp-v1.2.3")
    pyapp_dir.mkdir(parents=True)
    build_dir.joinpath("pyapp-source.tar.gz").touch()

    # create fake binary
    cargo_target = build_dir.joinpath("pyapp-v1.2.3/target/release")
    cargo_target.mkdir(parents=True)
    cargo_target.joinpath("pyapp").touch()

    runner = CliRunner()
    result = runner.invoke(cli, ["package"])
    assert result.exit_code == 0
    assert result.output.__contains__("Project successfully packaged.")

    sp_run_mock.assert_any_call(["rye", "build"], stdout=sp_devnull_mock)
    sp_run_mock.assert_called_with(
        ["cargo", "build", "--release"],
        cwd=pyapp_dir,
        stdout=sp_devnull_mock,
    )
