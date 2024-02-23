# Test building a project with PyApp.

import os
from pathlib import Path
import tarfile
import urllib.request

import rich_click as click
import pytest

from box.packager import PackageApp, PYAPP_SOURCE
from box.config import PyProjectParser, pyproject_writer
import box.utils as ut

# HELPER FUNCTIONS #


def create_pyapp_source(project_path: Path) -> Path:
    """Create a fake PyApp source code .tar.gz file.

    :param project_path: Path to the project folder.

    :return: Path to the fake PyApp source code .tar.gz file.
    """
    # create an empty file, put it into a tar.gz archive
    pyapp_folder = project_path.joinpath("pyapp-vx.y.z")
    pyapp_folder.mkdir()
    tmp_file = pyapp_folder.joinpath("tmp_file")
    tmp_file.touch()

    project_path.joinpath("build").mkdir(exist_ok=True)
    tar_name = Path("build/pyapp-source.tar.gz")

    with tarfile.open(tar_name, "w:gz") as tar:
        tar.add(pyapp_folder.name)

    return project_path.joinpath(tar_name)


# TESTS #


def test_cargo_not_found(rye_project, mocker):
    """Test that cargo not found raises an exception."""
    # mock $PATH to remove cargo
    mocker.patch.dict(os.environ, {"PATH": ""})
    with pytest.raises(click.ClickException):
        PackageApp()


def test_build_rye(rye_project, mocker):
    """Test that rye build is called and dist folder is found."""
    # mock subprocess.run
    sp_mock = mocker.patch("subprocess.run")

    packager = PackageApp()
    packager.build()

    sp_mock.assert_called_with(
        packager.builders["rye"], stdout=mocker.ANY, stderr=mocker.ANY
    )

    expected_path = rye_project.joinpath("dist")
    assert packager._dist_path == expected_path


def test_get_pyapp_extraction(rye_project, mocker):
    """Extract and set and path for PyApp source code."""
    mocker.patch.object(urllib.request, "urlretrieve")

    _ = create_pyapp_source(rye_project)

    packager = PackageApp()
    packager._get_pyapp()

    assert rye_project.joinpath("build/pyapp-vx.y.z").is_dir()
    assert rye_project.joinpath("build/pyapp-vx.y.z/tmp_file").is_file()

    assert packager._pyapp_path == rye_project.joinpath("build/pyapp-vx.y.z")


def test_get_pyapp_extraction_multiple_folders(rye_project, mocker):
    """Raise a warning if multiple pyapp folders are found."""
    mocker.patch.object(urllib.request, "urlretrieve")
    mocker.patch("tarfile.open")
    echo_mock = mocker.patch("box.formatters.warning")

    # create two pyapp folders in the build folder
    rye_project.joinpath("build/pyapp-v1.2.3").mkdir(parents=True)
    rye_project.joinpath("build/pyapp-v2.2.3").mkdir(parents=True)
    # create a fake source code file - tarfile is mocked
    rye_project.joinpath("build/pyapp-source.tar.gz").touch()

    packager = PackageApp()
    packager._get_pyapp()

    echo_mock.assert_called_with(
        "Multiple pyapp versions were. Using pyapp-v2.2.3. "
        "Consider cleaning the build folder with `box clean`."
    )

    assert packager._pyapp_path == rye_project.joinpath("build/pyapp-v2.2.3")


def test_get_pyapp_same_folder_exists(rye_project, mocker):
    """Do not extract source if the same PyApp folder already exists."""
    mocker.patch.object(urllib.request, "urlretrieve")

    tar_name = create_pyapp_source(rye_project)

    # unpack the tar file in the build folder
    with ut.set_dir(rye_project.joinpath("build")):
        with tarfile.open(tar_name, "r:gz") as tar:
            tar.extractall()

    # create a new file and modify the existing file in the pyapp folder
    new_file = rye_project.joinpath("build/pyapp-vx.y.z/tmp_file2")
    new_file.touch()
    existing_file = rye_project.joinpath("build/pyapp-vx.y.z/tmp_file")
    existing_file.write_text("test")

    packager = PackageApp()
    packager._get_pyapp()

    assert rye_project.joinpath("build/pyapp-vx.y.z/tmp_file").read_text() == "test"
    assert rye_project.joinpath("build/pyapp-vx.y.z/tmp_file2").is_file()


def test_get_pyapp_no_file_found(rye_project, mocker):
    """Raise an error if PyApp is not downloaded properly."""

    url_mock = mocker.patch.object(urllib.request, "urlretrieve")

    packager = PackageApp()
    with pytest.raises(click.ClickException) as e:
        packager._get_pyapp()

    assert e.value.args[0].__contains__("Error: no pyapp source code found")
    url_mock.assert_called_with(PYAPP_SOURCE, Path("pyapp-source.tar.gz"))


def test_get_pyapp_source_exists(rye_project, mocker):
    """Do not download from web if source already exists."""
    url_mock = mocker.patch.object(urllib.request, "urlretrieve")
    tar_mock = mocker.patch("tarfile.open")

    # create fake source code file
    rye_project.joinpath("build/").mkdir()
    rye_project.joinpath("build/pyapp-source.tar.gz").touch()

    packager = PackageApp()
    with pytest.raises(click.ClickException):  # raises an exception b/c no folder
        packager._get_pyapp()

    url_mock.assert_not_called()
    tar_mock.assert_called_with(Path("pyapp-source.tar.gz"), "r:gz")


def test_get_pyapp_wrong_no_pyapp_folder(rye_project, mocker):
    """Raise an error if PyApp is not extracted into a proper folder."""
    mocker.patch.object(urllib.request, "urlretrieve")
    mocker.patch("tarfile.open")

    # create a fake source code file - tarfile is mocked
    rye_project.joinpath("build/").mkdir()

    packager = PackageApp()

    with pytest.raises(click.ClickException) as e:
        packager._get_pyapp()

    assert e.value.args[0].__contains__("Error: no pyapp source code found")

    rye_project.joinpath("build/pyapp-source.tar.gz").touch()

    with pytest.raises(click.ClickException) as e:
        packager._get_pyapp()

    assert e.value.args[0].__contains__("Error: no pyapp source code folder found.")


@pytest.mark.parametrize("binary_extensions", [".exe", ""])
def test_package_pyapp_cargo_and_move(rye_project, mocker, binary_extensions):
    """Ensure cargo is called correctly and final binary moved to the right folder."""
    pyapp_path = rye_project.joinpath("build/pyapp-vx.y.z")
    cargo_binary_folder = pyapp_path.joinpath("target/release")
    cargo_binary_folder.mkdir(parents=True)

    pyapp_binary = cargo_binary_folder.joinpath("pyapp").with_suffix(binary_extensions)
    pyapp_binary.write_text("not really a binary")

    # mock subprocess.run
    sp_run_mock = mocker.patch("subprocess.run")
    sp_devnull_mock = mocker.patch("subprocess.DEVNULL")

    packager = PackageApp()
    packager._pyapp_path = pyapp_path
    packager._package_pyapp()

    sp_run_mock.assert_called_with(
        ["cargo", "build", "--release"],
        cwd=pyapp_path,
        stdout=sp_devnull_mock,
        stderr=sp_devnull_mock,
    )
    exp_binary = rye_project.joinpath(
        f"target/release/{rye_project.name}{binary_extensions}"
    )
    assert exp_binary.is_file()
    assert exp_binary.read_text() == "not really a binary"


@pytest.mark.parametrize("opt_deps", ["gui", None])
def test_set_env(rye_project, opt_deps, mocker):
    """Set environment for `PyApp` packaging."""
    config = PyProjectParser()
    exec_spec = config.app_entry

    # mock subprocess.run to avoid building
    mocker.patch("subprocess.run")
    rye_project.joinpath("dist").mkdir()
    dist_file = rye_project.joinpath(f"dist/{rye_project.name.lower()}-0.1.0.tar.gz")
    dist_file.touch()

    # write optional deps to the pyproject.toml
    if opt_deps:
        pyproject_writer("optional_deps", opt_deps)

    packager = PackageApp()
    packager.build()
    packager._set_env()

    package_name = rye_project.name.replace("-", "_").lower()
    assert os.environ["PYAPP_PROJECT_NAME"] == package_name
    assert os.environ["PYAPP_PROJECT_VERSION"] == "0.1.0"
    assert os.environ["PYAPP_PROJECT_PATH"] == str(dist_file)
    assert os.environ["PYAPP_EXEC_SPEC"] == exec_spec
    if opt_deps:
        assert os.environ["PYAPP_PIP_OPTIONAL_DEPS"] == opt_deps


def test_set_env_delete_existing(rye_project, mocker):
    """Delete existing `PYAPP` environmental variables."""
    var_name = "PYAPP_BLA_VARIABLE"
    var_value = "test"
    os.environ[var_name] = var_value

    packager = PackageApp()

    # set dist path to avoid error - not needed for this test
    packager._dist_path = rye_project

    packager._set_env()

    with pytest.raises(KeyError):
        _ = os.environ[var_name]
