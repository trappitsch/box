# Create an OS specific installer for GUI or CLI application.

import os
from pathlib import Path
import sys

import rich_click as click

from box import RELEASE_DIR_NAME
from box.installer_utils import linux_cli
from box.config import PyProjectParser
import box.formatters as fmt


class CreateInstaller:
    """Create an installer specific for the OS and depending on if GUI or CLI."""

    def __init__(self):
        """Initialize the installer creator."""
        self._config = PyProjectParser()
        self._installer_name = None

        if sys.platform.startswith("linux"):
            self._os = "Linux"
        elif sys.platform == "darwin":
            self._os = "macOS"
        elif sys.platform == "win32":
            self._os = "Windows"
        else:
            self._os = sys.platform

        self.release_file = self._check_release()

        self._mode = "GUI" if self._config.is_gui else "CLI"

        if self._os == "Linux" and self._mode == "CLI":
            self.linux_cli()
        else:
            self.unsupported_os_or_mode()

    @property
    def installer_name(self) -> str:
        """Return the name of the installer."""
        return self._installer_name

    def linux_cli(self) -> None:
        """Create a Linux CLI installer."""
        name_pkg = self._config.name_pkg
        version = self._config.version

        bash_part = linux_cli.create_bash_installer(name_pkg, version)

        with open(self.release_file, "rb") as f:
            binary_part = f.read()

        # Write the installer file
        installer_file = Path(RELEASE_DIR_NAME).joinpath(
            f"{name_pkg}-v{version}-linux.sh"
        )
        with open(installer_file, "wb") as f:
            f.write(bash_part.encode("utf-8"))
            f.write(binary_part)

        self._installer_name = installer_file.name

        # make installer executable
        mode = os.stat(installer_file).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(installer_file, mode)

    def unsupported_os_or_mode(self):
        """Print a message for unsupported OS or mode."""
        fmt.warning(
            f"Creating an installer for a {self._mode} is \
            currently not supported on {self._os}."
        )

    def _check_release(self) -> Path:
        """Check if release exists, if not, throw error.

        :return: Path to the release.
        """
        release_file = Path(RELEASE_DIR_NAME).joinpath(self._config.name_pkg)
        if not release_file.exists():
            raise click.ClickException("No release found. Run `box package` first.")
        return release_file
