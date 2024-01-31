# Test building a project with PyApp.

import os

import click
import pytest

from box.packager import PackageApp


def test_cargo_not_found(mocker):
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

    sp_mock.assert_called_with(["rye", "build"], stdout=mocker.ANY)

    expected_path = rye_project.joinpath("dist")
    assert packager._dist_path == expected_path


def test_get_pyapp(rye_project, mocker):
    """Test that PyApp is downloaded and extracted."""
    mocker.patch("urllib.request")

    # todo: create some tar.gz package in here to fake unpack
    # todo: make sure that we unpack the tar.gz to correct folder

    packager = PackageApp()
    packager._get_pyapp()


@pytest.mark.long
def test_set_env(rye_project):
    """Set environment for `PyApp` packaging."""
    packager = PackageApp()
    packager.build()
    packager.set_env()

    dist_file = rye_project.joinpath(f"dist/{rye_project.name}-0.1.0.tar.gz")

    package_name = rye_project.name.replace("-", "_")
    assert os.environ["PYAPP_PROJECT_NAME"] == package_name
    assert os.environ["PYAPP_PROJECT_VERSION"] == "0.1.0"
    assert os.environ["PYAPP_PROJECT_PATH"] == str(dist_file)
    assert os.environ["PYAPP_EXEC_SPEC"] == f"{package_name}:run"


def test_set_env_delete_existing(rye_project, mocker):
    """Delete existing `PYAPP` environmental variables."""
    var_name = "PYAPP_BLA_VARIABLE"
    var_value = "test"
    os.environ[var_name] = var_value

    packager = PackageApp()

    # set dist path to avoid error - not needed for this test
    packager._dist_path = rye_project

    packager.set_env()

    with pytest.raises(KeyError):
        _ = os.environ[var_name]
