# Build the project with PyApp

import os
from pathlib import Path
import subprocess
import urllib.request

import click

from box import BUILD_DIR_NAME, RELEASE_DIR_NAME
from box.config import PyProjectParser
import box.utils as ut

PYAPP_SOURCE = "https://github.com/ofek/pyapp/releases/latest/download/source.tar.gz"


class PackageApp:
    """Package the project with PyApp."""

    def __init__(self):
        """Initialize the PackageApp class."""
        # self._builder = box_config.builder
        self._dist_path = None
        self._pyapp_path = None

        self._build_dir = Path.cwd().joinpath(BUILD_DIR_NAME)
        self._release_dir = Path.cwd().joinpath(RELEASE_DIR_NAME)
        self._build_dir.mkdir(exist_ok=True)
        self._release_dir.mkdir(parents=True, exist_ok=True)

        self._config = PyProjectParser()

        self._check_requirements()

    def build(self):
        """Build the project with PyApp."""
        builder = self._config.builder
        if builder == "rye":
            self._build_rye()
        else:
            raise ValueError("Unknown builder")

        click.echo(f"Project built with {builder}.")

    def set_env(self):
        """Set the environment for packaging the project with PyApp."""
        # clean all variables startying with `PYAPP` from environment
        for var in list(os.environ):
            if var.startswith("PYAPP"):
                del os.environ[var]

        # find the tar.gz file in dist folder with correct version number
        dist_file = None
        for file in self._dist_path.iterdir():
            if file.name.__contains__(self._config.version):
                dist_file = file
                break

        # set variables
        os.environ["PYAPP_PROJECT_NAME"] = self._config.name_pkg
        os.environ["PYAPP_PROJECT_VERSION"] = self._config.version
        os.environ["PYAPP_PROJECT_PATH"] = str(dist_file)
        os.environ["PYAPP_EXEC_SPEC"] = f"{self._config.name_pkg}:run"

    def _build_rye(self):
        """Build the project with rye."""
        subprocess.run(["rye", "build"], stdout=subprocess.DEVNULL)
        self._dist_path = Path.cwd().joinpath("dist")

    def _get_pyapp(self):
        """Download the PyApp source code and extract to `build/pyapp-latest` folder.

        Download and or extraction are skipped if folder already exists.

        # todo: implement clean calls
        """
        tar_name = "pyapp-source.tar.gz"

        with ut.set_dir(self._build_dir):
            # if not
            urllib.request.urlretrieve(PYAPP_SOURCE, "pyapp-source.tar.gz")

            # # extract the source with tarfile package as pyapp-latest
            # with tarfile.open("pyapp-source.tar.gz", "r:gz") as tar:
            #     tar.extractall()
            #
            # # find the name of the pyapp folder and return it
            #
            # for file in Path(".").iterdir():
            #     if file.is_dir() and file.name.startswith("pyapp-"):
            #         return file

    # STATIC METHODS #
    @staticmethod
    def _check_requirements():
        """Check if all requirements are installed."""
        # check for cargo
        try:
            subprocess.run(
                ["cargo", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            raise click.ClickException(
                "Error: cargo not found. Please install cargo and try again."
            )
