# Create an OS specific installer for GUI or CLI application.

import sys

from box.config import PyProjectParser
import box.formatters as fmt


class CreateInstaller:
    """Create an installer specific for the OS and depending if GUI or CLI."""

    def __init__(self):
        """Initialize the installer creator."""
        self._config = PyProjectParser()

        if sys.platform.startswith("linux"):
            self._os = "Linux"
        elif sys.platform == "darwin":
            self._os = "macos"
        elif sys.platform == "win32":
            self._os = "Windows"
        else:
            self._os = sys.platform

        self._mode = "GUI" if self._config.is_gui else "CLI"

        if self._os == "Linux" and self._mode == "CLI":
            self.linux_cli()
        else:
            self.unsupported_os_or_mode()

    def linux_cli(self) -> None:
        """Create a Linux CLI installer."""
        fmt.info("Creating a Linux CLI installer...")

    def unsupported_os_or_mode(self):
        """Print a message for unsupported OS or mode."""
        fmt.error(
            f"Creating an installer for a {self.mode} is \
            currently not supported on {self.os}."
        )
