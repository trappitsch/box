# Build the project with PyApp

import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

import rich_click as click

from box import BUILD_DIR_NAME, RELEASE_DIR_NAME
from box.config import PyProjectParser
import box.formatters as fmt
import box.utils as ut

PYAPP_SOURCE = "https://github.com/ofek/pyapp/releases/latest/download/source.tar.gz"


class PackageApp:
    """Package the project with PyApp."""

    def __init__(self, verbose=False):
        """Initialize the PackageApp class.

        :param verbose: bool, flag to enable verbose mode.
        """
        self.subp_kwargs = {}
        if not verbose:
            self.subp_kwargs["stdout"] = subprocess.DEVNULL

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
        fmt.info(f"Building project with {builder}...")
        if builder == "rye":
            self._build_rye()
        else:
            raise ValueError("Unknown builder")

        fmt.success(f"Project built with {builder}.")

    def package(self):
        """Package the project with PyApp."""
        fmt.info("Hold on, packaging the project with PyApp...")
        self._get_pyapp()
        self._set_env()
        self._package_pyapp()
        fmt.success("Project packaged with PyApp.")

    def _build_rye(self):
        """Build the project with rye."""
        subprocess.run(["rye", "build"], **self.subp_kwargs)

        self._dist_path = Path.cwd().joinpath("dist")

    def _get_pyapp(self):
        """Download the PyApp source code and extract to `build/pyapp-latest` folder.

        Download and or extraction are skipped if folder already exists.

        :raises: `click.ClickException` if no pyapp source code is found
        """
        tar_name = Path("pyapp-source.tar.gz")

        with ut.set_dir(self._build_dir):
            if not tar_name.is_file():
                urllib.request.urlretrieve(PYAPP_SOURCE, tar_name)

            if not tar_name.is_file():
                raise click.ClickException(
                    "Error: no pyapp source code found. "
                    "Please check your internet connection and try again."
                )

            # check if pyapp source code is already extracted
            all_pyapp_folders = []
            for file in Path(".").iterdir():
                if file.is_dir() and file.name.startswith("pyapp-"):
                    all_pyapp_folders.append(file)

            with tarfile.open(tar_name, "r:gz") as tar:
                tarfile_members = tar.getmembers()

                # only extract if the folder in there (first entry) does not already exist
                folder_exists = False
                new_folder = tarfile_members[0].name
                for folder in all_pyapp_folders:
                    if folder.name == new_folder:
                        folder_exists = True
                        break

                # extract the source with tarfile package as pyapp-latest
                if not folder_exists:
                    tar.extractall()
                    if "pyapp-" in new_folder:
                        all_pyapp_folders.append(Path(new_folder))

            # find the name of the pyapp folder and return it
            if len(all_pyapp_folders) == 1:
                self._pyapp_path = all_pyapp_folders[0].absolute()
            elif len(all_pyapp_folders) > 1:
                all_pyapp_folders.sort(key=lambda x: x.stem)
                self._pyapp_path = all_pyapp_folders[-1].absolute()
                fmt.warning(
                    "Multiple pyapp versions were. "
                    f"Using {self._pyapp_path.name}. "
                    "Consider cleaning the build folder with `box clean`."
                )
            else:  # so there's no folder, exit with error
                raise click.ClickException(
                    "Error: no pyapp source code folder found. "
                    "Consider cleaning your project with `box clean`."
                )

    def _package_pyapp(self):
        """Package the PyApp.

        Environment must already be setup and PyApp source code must already be
        extracted in `self._pyapp_path`.
        """
        subprocess.run(
            ["cargo", "build", "--release"], cwd=self._pyapp_path, **self.subp_kwargs
        )

        # create release folder if it does not exist
        self._release_dir.mkdir(exist_ok=True, parents=True)

        # move package to dev folder and rename it to module_name
        shutil.move(
            self._pyapp_path.joinpath("target/release/pyapp"),
            self._release_dir.joinpath(self._config.name_pkg),
        )

    def _set_env(self):
        """Set the environment for packaging the project with PyApp."""
        # clean all variables startying with `PYAPP` from environment
        for var in list(os.environ):
            if var.startswith("PYAPP"):
                del os.environ[var]

        # find the tar.gz file in dist folder with correct version number
        dist_file = None
        for file in self._dist_path.iterdir():
            if self._config.version in file.name and file.suffix == ".gz":
                dist_file = file
                break

        # set variables
        os.environ["PYAPP_PROJECT_NAME"] = self._config.name_pkg
        os.environ["PYAPP_PROJECT_VERSION"] = self._config.version
        os.environ["PYAPP_PROJECT_PATH"] = str(dist_file)
        # fixme: this whole thing is a hack. give options for entry, see PyApp docs
        os.environ["PYAPP_EXEC_SPEC"] = self._config.app_entry

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
