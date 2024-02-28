# Build the project with PyApp

import os
from pathlib import Path
import shutil
import subprocess
import tarfile
from typing import List, Union
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

    def package(self, local_source: Union[Path, str] = None):
        """Package the project with PyApp.

        :param local_source: Path to the local source. Can be folder or .tar.gz archive.
        """
        fmt.info("Hold on, packaging the project with PyApp...")
        self._build_dir.mkdir(exist_ok=True)
        self._release_dir.mkdir(parents=True, exist_ok=True)
        self._get_pyapp(local_source=local_source)
        self._set_env()
        self._package_pyapp()

    def _get_pyapp(self, local_source: Union[Path, str] = None):
        """Download the PyApp source code and extract to `build/pyapp-latest` folder.

        Download and or extraction are skipped if folder already exists.

        :param local_source: Path to the local source. Can be folder or .tar.gz archive.

        :raises: `click.ClickException` if no pyapp source code is found
        """
        tar_name = Path("pyapp-source.tar.gz")

        if isinstance(local_source, str):
            local_source = Path(local_source)

        with ut.set_dir(self._build_dir):
            if local_source:  # copy local source if provided
                if local_source.suffix == ".gz" and local_source.is_file():
                    shutil.copy(local_source, tar_name)
                elif local_source.is_dir():
                    shutil.copytree(
                        local_source, self._build_dir.joinpath(local_source.name)
                    )
                else:
                    raise click.ClickException(
                        "Error: invalid local pyapp source code. "
                        "Please provide a valid folder or a .tar.gz archive."
                    )

            else:  # no local source
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

            # extract the source code if we didn't just copy a local folder
            if not local_source or local_source.suffix == ".gz":
                with tarfile.open(tar_name, "r:gz") as tar:
                    tarfile_members = tar.getmembers()

                    # only extract if the folder in archive does not already exist
                    folder_exists = False
                    new_folder = tarfile_members[0].name
                    for folder in all_pyapp_folders:
                        if folder.name == new_folder:
                            folder_exists = True
                            break

                    # extract the source with tarfile package
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
        binary_path = self._pyapp_path.joinpath("target/release/pyapp")
        suffix = ""
        if not binary_path.is_file():
            binary_path = binary_path.with_suffix(".exe")  # we are probably on windows!
            suffix = ".exe"
        self._binary_name = self._release_dir.joinpath(
            self.config.name_pkg
        ).with_suffix(suffix)
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

        # set variables
        os.environ["PYAPP_PROJECT_NAME"] = self.config.name_pkg
        os.environ["PYAPP_PROJECT_VERSION"] = self.config.version
        os.environ["PYAPP_PROJECT_PATH"] = str(dist_file)
        # fixme: this whole thing is a hack. give options for entry, see PyApp docs
        os.environ["PYAPP_EXEC_SPEC"] = self.config.app_entry
        os.environ["PYAPP_PYTHON_VERSION"] = py_version
        if value := self.config.optional_dependencies:
            os.environ["PYAPP_PIP_OPTIONAL_DEPS"] = value

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
