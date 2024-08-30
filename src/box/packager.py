# Build the project with PyApp

import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path
from typing import List, Union

import rich_click as click

import box.formatters as fmt
import box.utils as ut
from box import BUILD_DIR_NAME, RELEASE_DIR_NAME
from box.config import PyProjectParser

PYAPP_SOURCE_URL = "https://github.com/ofek/pyapp/releases/"
PYAPP_SOURCE_NAME = "source.tar.gz"
PYAPP_SOURCE_LATEST = f"{PYAPP_SOURCE_URL}latest/download/{PYAPP_SOURCE_NAME}"


class PackageApp:
    """Package the project with PyApp."""

    def __init__(self, verbose=False):
        """Initialize the PackageApp class.

        :param verbose: bool, flag to enable verbose mode.
        """
        self.subp_kwargs = {}
        if not verbose:
            self.subp_kwargs["stdout"] = subprocess.DEVNULL
            self.subp_kwargs["stderr"] = subprocess.DEVNULL

        self._binary_name = None  # name of the binary file at the end of packaging

        # self._builder = box_config.builder
        self._dist_path = Path.cwd().joinpath("dist")
        self._pyapp_path = None

        # supported builders
        self._builders = {
            "rye": ["rye", "build", "--out", f"{self._dist_path}", "--sdist"],
            "hatch": ["hatch", "build", "-t", "sdist"],
            "pdm": ["pdm", "build", "--no-wheel", "-d", f"{self._dist_path}"],
            "build": [
                ut.cmd_python(),
                "-m",
                "build",
                "--sdist",
                "--outdir",
                f"{self._dist_path}",
            ],
            "flit": ["flit", "build", "--format", "sdist"],
        }

        self._build_dir = Path.cwd().joinpath(BUILD_DIR_NAME)
        self._release_dir = Path.cwd().joinpath(RELEASE_DIR_NAME)

        self._config = None

    @property
    def builders(self) -> List:
        """Return a list of supported builders and their commands."""
        return list(self._builders.keys())

    @property
    def binary_name(self):
        return self._binary_name

    @property
    def config(self) -> PyProjectParser:
        """Return the project configuration."""
        if self._config is None:
            self._config = PyProjectParser()
        return self._config

    def build(self):
        """Build the project with PyApp."""
        builder = self.config.builder
        fmt.info(f"Building project with {builder}...")
        try:
            subprocess.run(self._builders[builder], **self.subp_kwargs)
        except KeyError as e:
            raise KeyError(f"Unknown {builder=}") from e

        fmt.success(f"Project built with {builder}.")

    def package(self, pyapp_version="latest", local_source: Union[Path, str] = None):
        """Package the project with PyApp.

        :param pyapp_version: PyApp version to download.
        :param local_source: Path to the local source. Can be folder or .tar.gz archive.
        """
        fmt.info("Hold on, packaging the project with PyApp...")
        self._build_dir.mkdir(exist_ok=True)
        self._release_dir.mkdir(parents=True, exist_ok=True)
        self._get_pyapp(pyapp_version, local_source=local_source)
        self._set_env()
        self._package_pyapp()

    def _get_pyapp(
        self, pyapp_version: str = "latest", local_source: Union[Path, str] = None
    ):
        """Download the PyApp source code and extract to `build/pyapp-latest` folder.

        Download and or extraction are skipped if folder already exists.

        :param pyapp_version: PyApp version to download.
        :param local_source: Path to the local source. Can be folder or .tar.gz archive.

        :raises: `click.ClickException` if no pyapp source code is found
        """
        tar_name = Path("pyapp-source.tar.gz")
        local_source_destination = "pyapp-local"
        local_source_exists = False

        if isinstance(local_source, str):
            local_source = Path(local_source)

        with ut.set_dir(self._build_dir):
            if local_source:  # copy local source if provided
                if local_source.suffix == ".gz" and local_source.is_file():
                    shutil.copy(local_source, tar_name)
                elif local_source.is_dir():
                    if Path(local_source_destination).is_dir():
                        fmt.warning(
                            "Local source folder already copied. "
                            "If you want to copy again, please clean the project first."
                        )
                    else:
                        shutil.copytree(
                            local_source,
                            self._build_dir.joinpath(local_source_destination),
                        )
                else:
                    raise click.ClickException(
                        "Error: invalid local pyapp source code. "
                        "Please provide a valid folder or a .tar.gz archive."
                    )

            else:  # no local source
                if Path(local_source_destination).is_dir():
                    local_source_exists = True
                    fmt.info("Using existing local pyapp source.")
                elif not tar_name.is_file():
                    if pyapp_version == "latest":
                        pyapp_source = PYAPP_SOURCE_LATEST
                    else:
                        pyapp_source = (
                            f"{PYAPP_SOURCE_URL}download/{pyapp_version}/"
                            f"{PYAPP_SOURCE_NAME}"
                        )
                    urllib.request.urlretrieve(pyapp_source, tar_name)

                    if not tar_name.is_file():
                        raise click.ClickException(
                            f"Error: no pyapp source code found. "
                            f"Check if version {pyapp_version} exists and if your "
                            f"internet connection is working."
                        )

            # check if pyapp source code is already extracted
            all_pyapp_folders = []
            for file in Path(".").iterdir():
                if file.is_dir() and file.name.startswith("pyapp-"):
                    all_pyapp_folders.append(file)

            # extract the source code if we didn't just copy a local folder
            if not local_source_exists:
                if not local_source or local_source.suffix == ".gz":
                    with tarfile.open(tar_name, "r:gz") as tar:
                        tarfile_members = tar.getmembers()

                        # only extract if not existing and no local source!
                        folder_exists = False
                        new_folder = tarfile_members[0].name
                        for folder in all_pyapp_folders:
                            if (
                                folder.name == new_folder
                                or folder.name == local_source_destination
                            ):
                                folder_exists = True
                                break

                        # extract the source with tarfile package
                        if not folder_exists:
                            tar.extractall()
                            if "pyapp-" in new_folder:
                                all_pyapp_folders.append(Path(new_folder))

                        # if local source, rename the extracted folder
                        if local_source:
                            shutil.move(
                                new_folder,
                                local_source_destination,
                            )

            # find the name of the pyapp folder and return it
            if len(all_pyapp_folders) == 1:
                self._pyapp_path = all_pyapp_folders[0].absolute()
            elif len(all_pyapp_folders) > 1:
                all_pyapp_folders.sort(key=lambda x: x.stem)
                if Path(local_source_destination).is_dir():
                    self._pyapp_path = self._build_dir.joinpath(
                        local_source_destination
                    )
                else:
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
        binary_path = self._pyapp_path.joinpath("target/release/pyapp")
        if sys.platform == "win32":
            binary_path = binary_path.with_suffix(".exe")

        if not binary_path.is_file():
            raise click.ClickException(
                "No binary created. Please check build process with `box package -v`."
            )

        self._binary_name = self._release_dir.joinpath(self.config.name).with_suffix(
            binary_path.suffix
        )
        shutil.move(binary_path, self._binary_name)

    def _set_env(self):
        """Set the environment for packaging the project with PyApp."""
        # clean all variables startying with `PYAPP` from environment
        for var in list(os.environ):
            if var.startswith("PYAPP"):
                del os.environ[var]

        # find the tar.gz file in dist folder with correct version number
        dist_file = None
        for file in self._dist_path.iterdir():
            if self.config.version in file.name and file.suffix == ".gz":
                dist_file = file
                break

        # get the python version or set to default
        py_version = self.config.python_version or ut.PYAPP_PYTHON_VERSIONS[-1]

        # set variable name for app_entry
        app_entry_type = self.config.app_entry_type
        var_app_entry = f"PYAPP_EXEC_{app_entry_type.upper()}"

        # set variables
        os.environ["PYAPP_PROJECT_NAME"] = self.config.name_pkg
        os.environ["PYAPP_PROJECT_VERSION"] = self.config.version
        os.environ["PYAPP_PROJECT_PATH"] = str(dist_file)
        os.environ[var_app_entry] = self.config.app_entry
        os.environ["PYAPP_PYTHON_VERSION"] = py_version
        if value := self.config.optional_dependencies:
            os.environ["PYAPP_PROJECT_FEATURES"] = value
        optional_pyapp_vars = self.config.env_vars
        for key, value in optional_pyapp_vars.items():
            os.environ[key] = value
        if self.config.is_gui:
            os.environ["PYAPP_IS_GUI"] = "1"

    # STATIC METHODS #
    @staticmethod
    def check_requirements():
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
