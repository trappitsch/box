# CLI tests for cleaning the project folder

from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner

from box.cli import cli


def setup_folders(project_folder: Path) -> List[Path]:
    """Setup `dist`, `build`, `target` folder.

    The `dist` and `target` folder get a file each. The `build` folder gets a
    dummy file for pyapp source and a pyapp project folder.

    :param project_folder: Path to the project folder.

    :return: Paths to the `dist`, `build`, `target` folders.
    """
    dist_folder = project_folder.joinpath("dist")
    dist_folder.mkdir()
    build_folder = project_folder.joinpath("build")
    build_folder.mkdir()
    target_folder = project_folder.joinpath("target")
    target_folder.mkdir()

    # create a file in each folder to ensure deleting is recursively
    dist_folder.joinpath("tmp_file").touch()
    target_folder.joinpath("tmp_file").touch()

    # create a dummy pyapp source code folder and source code .tar.gz file
    build_folder.joinpath("pyapp-v1.2.3").mkdir()
    build_folder.joinpath("pyapp-source.tar.gz").touch()

    return dist_folder, build_folder, target_folder


def test_clean(rye_project):
    """Clean the project folder."""
    folders = setup_folders(rye_project)

    runner = CliRunner()
    result = runner.invoke(cli, ["clean"])

    for folder in folders:
        assert not folder.exists()

    assert result.exit_code == 0
    assert "The whole project was cleaned." in result.output


@pytest.mark.parametrize(
    "option",
    [
        "-d",
        "--dist",
        "-t",
        "--target",
        "-b",
        "--build",
    ],
)
def test_clean_folder(rye_project, option):
    """Only clean one specific folder."""
    folders = setup_folders(rye_project)

    # index of folder that was deleted
    option_first_letter = option.lstrip("-")[0]
    if option_first_letter == "d":
        index = 0
        folder_name = "dist"
    elif option_first_letter == "b":
        index = 1
        folder_name = "build"
    elif option_first_letter == "t":
        index = 2
        folder_name = "target"
    else:
        assert False

    runner = CliRunner()
    result = runner.invoke(cli, ["clean", option])

    for it, folder in enumerate(folders):
        if it == index:
            assert not folder.exists()
        else:
            assert folder.exists()

    assert result.exit_code == 0
    assert f"Folder(s) {folder_name} cleaned." in result.output


def test_clean_multiple_folders(rye_project):
    """Clean dist and target folders."""
    dist, build, target = setup_folders(rye_project)

    runner = CliRunner()
    result = runner.invoke(cli, ["clean", "-dt"])

    assert not dist.exists()
    assert not target.exists()
    assert build.exists()

    assert result.exit_code == 0
    assert "Folder(s) dist, target cleaned." in result.output


@pytest.mark.parametrize("init_folder", [True, False])
def test_clean_no_pyproject(tmp_path_chdir, rye_project_no_box, init_folder):
    """Display a message that not in a box folder and do nothing."""
    proj_folder = rye_project_no_box if init_folder else tmp_path_chdir
    dist_dir = proj_folder.joinpath("dist")
    dist_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(cli, ["clean"])

    assert dist_dir.exists()
    assert result.exit_code == 1
    assert "This is not a box project." in result.output


def test_clean_nothing_to_do(rye_project):
    """State nothing to clean if already clean."""
    runner = CliRunner()
    result = runner.invoke(cli, ["clean"])
    assert "Nothing to clean." in result.output


@pytest.mark.parametrize(
    "option", ["-p", "--pyapp-folder", "-s", "--source-pyapp", "-ps"]
)
def test_clean_pyapp(rye_project, option):
    """Clean up only pyapp build folder, either tar.gz, pyapp-folder(s), or both."""
    _, build, _ = setup_folders(rye_project)
    source = build.joinpath("pyapp-source.tar.gz")
    build.joinpath("pyapp-latest").mkdir()

    if option == "-ps":
        source_exists = False
        pyapp_exists = False
    else:
        option_first_letter = option.lstrip("-")[0]
        source_exists = False if option_first_letter == "s" else True
        pyapp_exists = False if option_first_letter == "p" else True

    runner = CliRunner()
    result = runner.invoke(cli, ["clean", option])

    assert source.exists() is source_exists
    if not pyapp_exists:
        # assure there are no pyapp folders left, but source can still be there!
        for fld in build.iterdir():
            if fld.is_dir() and fld.name.startswith("pyapp-"):
                assert False

    assert result.exit_code == 0

    if not source_exists:
        assert "pyapp-source.tar.gz" in result.output
    if not pyapp_exists:
        assert "pyapp folder(s)" in result.output

    assert build.exists()


@pytest.mark.parametrize("option", ["-sb", "-pb"])
def test_clean_pyapp_ignor_t_flag(rye_project, option):
    """Clean up pyapp folder(s) and ignore the set target flag."""
    _, build, _ = setup_folders(rye_project)

    runner = CliRunner()
    result = runner.invoke(cli, ["clean", option])

    assert result.exit_code == 0
    assert "Info: Build folder flag `-b`, `--build` ignored." in result.output

    assert build.exists()
