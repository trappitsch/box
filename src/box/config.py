# Parse the pyproject.toml file

from pathlib import Path
from typing import Any, Dict

import tomlkit


class PyProjectParser:
    """Parse the pyproject.toml file in the current folder."""

    def __init__(self):
        """Initialize the PyProjectParser."""
        with open("pyproject.toml", "rb") as f:
            self._pyproject = tomlkit.load(f)

        try:
            self._project = self._pyproject["project"]
        except KeyError as err:  # re-raise error with further error message
            raise KeyError("Not a valid pyproject.toml file") from err

    @property
    def app_entry(self):
        """Return the box-saved app entry point."""
        return self._pyproject["tool"]["box"]["app_entry"]

    @property
    def builder(self) -> str:
        """Return the builder of the project."""
        return self._pyproject["tool"]["box"]["builder"]

    @property
    def is_box_project(self):
        """Return if this folder is a box project or not."""
        try:
            _ = self._pyproject["tool"]["box"]
            return True
        except KeyError:
            return False

    @property
    def name(self) -> str:
        """Return the name of the project."""
        return self._project["name"]

    @property
    def name_pkg(self) -> str:
        """Return the name of the package (project name with '-' replaced by '_')."""
        return self.name.replace("-", "_")

    @property
    def possible_app_entries(self) -> Dict:
        """Return [project.gui-scripts] or [project.scripts] entry if available.

        If no entry is available, return None. If more than one entry available,
        return a list of all entries.

        :return: A list of possible entry points or None.
        """
        possible_entries = {}
        try:
            possible_entries["gui-scripts"] = self._project["gui-scripts"]
        except KeyError:
            pass
        try:
            possible_entries["scripts"] = self._project["scripts"]
        except KeyError:
            pass
        return possible_entries

    @property
    def rye(self) -> dict:
        """Return the rye configuration of the project."""
        return self._pyproject["tool"]["rye"]

    @property
    def version(self) -> str:
        """Return the version of the project."""
        return self._project["version"]


def pyproject_writer(key: str, value: Any) -> None:
    """Modify the existing `pyproject.toml` file using `tomlkit`.

    Project specific, the table [tools.box] is used. If the table does not exist,
    it is created. If the key does not exist, it is created. If the key exists,
    it is overwritten.
    """
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.is_file():
        raise FileNotFoundError("No `pyproject.toml` file found in current folder.")

    with open(pyproject_file, "rb") as f:
        doc = tomlkit.load(f)

    try:
        tool_table = tomlkit.table(True)
        box_table = tomlkit.table()
        tool_table.append("box", box_table)
        doc.append("tool", tool_table)
    except tomlkit.exceptions.KeyAlreadyPresent:
        box_table = doc["tool"]["box"]

    box_table.update({key: value})

    with open(pyproject_file, "w", newline="\n") as f:
        tomlkit.dump(doc, f)
