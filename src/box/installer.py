# Create an OS specific installer for GUI or CLI application.

import os
from pathlib import Path
import subprocess
import sys

import rich_click as click

from box import RELEASE_DIR_NAME
from box.config import PyProjectParser
import box.formatters as fmt
import box.utils as ut


class CreateInstaller:
    """Create an installer specific for the OS and depending on if GUI or CLI."""

    def __init__(self, verbose: bool = False):
        """Initialize the installer creator.

        :param verbose: If True, print verbose output.
        """
        self._config = PyProjectParser()
        self._installer_name = None

        self.subp_kwargs = {}
        if not verbose:
            self.subp_kwargs["stdout"] = subprocess.DEVNULL
            self.subp_kwargs["stderr"] = subprocess.DEVNULL

        if sys.platform.startswith("linux"):
            self._os = "Linux"
        elif sys.platform == "darwin":
            self._os = "macOS"
        elif sys.platform == "win32":
            self._os = "Windows"
        else:
            self._os = sys.platform

        self._release_file = None
        self._mode = "GUI" if self._config.is_gui else "CLI"

    @property
    def installer_name(self) -> str:
        """Return the name of the installer."""
        return self._installer_name

    def create_installer(self):
        """Create the actual installer based on the OS and mode."""
        self._release_file = self._check_release()

        if self._os == "Linux" and self._mode == "CLI":
            self.linux_cli()
        elif self._os == "Linux" and self._mode == "GUI":
            self.linux_gui()
        elif self._os == "Windows" and self._mode == "CLI":
            self.windows_cli()
        elif self._os == "Windows" and self._mode == "GUI":
            self.windows_gui()
        else:
            self.unsupported_os_or_mode()

    def linux_cli(self) -> None:
        """Create a Linux CLI installer."""
        from box.installer_utils.linux_hlp import create_bash_installer_cli

        name = self._config.name
        version = self._config.version

        bash_part = create_bash_installer_cli(name, version)

        with open(self._release_file, "rb") as f:
            binary_part = f.read()

        # Write the installer file
        installer_file = Path(RELEASE_DIR_NAME).joinpath(f"{name}-v{version}-linux.sh")
        with open(installer_file, "wb") as f:
            f.write(bash_part.encode("utf-8"))
            f.write(binary_part)

        self._installer_name = installer_file.name

        # make installer executable
        mode = os.stat(installer_file).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(installer_file, mode)

    def linux_gui(self) -> None:
        """Create a Linux GUI installer."""
        from box.installer_utils.linux_hlp import create_bash_installer_gui

        name = self._config.name
        version = self._config.version
        icon = get_icon()
        icon_name = icon.name

        bash_part = create_bash_installer_gui(name, version, icon_name)

        with open(self._release_file, "rb") as f:
            binary_part = f.read()

        with open(icon, "rb") as f:
            icon_part = f.read()

        installer_file = Path(RELEASE_DIR_NAME).joinpath(f"{name}-v{version}-linux.sh")
        with open(installer_file, "wb") as f:
            f.write(bash_part.encode("utf-8"))
            f.write(binary_part)
            f.write(b"\n#__ICON_BINARY__\n")
            f.write(icon_part)

        self._installer_name = installer_file.name

        # make installer executable
        mode = os.stat(installer_file).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(installer_file, mode)

    def unsupported_os_or_mode(self):
        """Print a message for unsupported OS or mode."""
        fmt.warning(
            f"Creating an installer for a {self._mode} is "
            f"currently not supported on {self._os}."
        )

    def windows_cli(self):
        """Create a Windows CLI installer."""
        self._check_makensis()

        from box.installer_utils.windows_hlp import nsis_cli_script

        name = self._config.name
        version = self._config.version

        installer_name = f"{name}-v{version}-win.exe"

        with ut.set_dir(RELEASE_DIR_NAME):
            nsis_script_name = Path("make_installer.nsi")
            with open(nsis_script_name, "w") as f:
                f.write(
                    nsis_cli_script(
                        name,
                        installer_name,
                        self._config.author,
                        self._config.version,
                        self._release_file,
                    )
                )

            # make the installer
            subprocess.run(["makensis", nsis_script_name], **self.subp_kwargs)

            nsis_script_name.unlink()

        self._installer_name = installer_name

    def windows_gui(self):
        """Create a Windows GUI installer."""
        self._check_makensis()

        from box.installer_utils.windows_hlp import nsis_gui_script

        name = self._config.name
        version = self._config.version
        icon = get_icon("ico")

        installer_name = f"{name}-v{version}-win.exe"

        with ut.set_dir(RELEASE_DIR_NAME):
            nsis_script_name = Path("make_installer.nsi")
            with open(nsis_script_name, "w") as f:
                f.write(
                    nsis_gui_script(
                        name,
                        installer_name,
                        self._config.author,
                        self._config.version,
                        self._release_file,
                        icon,
                    )
                )

            # make the installer
            subprocess.run(["makensis", nsis_script_name], **self.subp_kwargs)

            nsis_script_name.unlink()

        self._installer_name = installer_name

    @staticmethod
    def _check_makensis():
        """Check if NSIS is installed correctly and available on the path."""
        try:
            subprocess.run(
                ["makensis", "-VERSION"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            raise click.ClickException(
                "NSIS is not installed or not available on the PATH. "
                "Please install NSIS and try again. "
                "For mor info, go to https://nsis.sourceforge.io"
            )

    def _check_release(self) -> Path:
        """Check if release exists, if not, throw error.

        :return: Path to the release.
        """
        release_file = Path(RELEASE_DIR_NAME).joinpath(self._config.name)

        if sys.platform == "win32":
            release_file = release_file.with_suffix(".exe")

        if not release_file.exists():
            raise click.ClickException("No release found. Run `box package` first.")
        return release_file


def get_icon(suffix: str = None) -> Path:
    """Return the icon file path.

    If no suffix is provided, the following priorites will be returned (depending
    on file availability):
    - icon.svg
    - icon.png
    - icon.jpg
    - icon.jpeg

    Note: Windows `.ico` files must be called out explicitly.

    :param suffix: The suffix of the icon file.

    :return: The path to the icon file.

    :raises ClickException: If no icon file is found.
    """
    icon_file = Path.cwd().joinpath("assets/icon")

    suffixes = ["svg", "png", "jpg", "jpeg"]
    if suffix:
        suffixes = [suffix]  # overwrite exisiting and only check this.

    for suffix in suffixes:
        icon_file = icon_file.with_suffix(f".{suffix}")
        if icon_file.exists():
            return icon_file

    raise click.ClickException(
        f"No icon file found. Please provide an icon file. "
        f"Valid formats are {', '.join(suffixes)}."
    )
