# Parse the pyproject.toml file

from pathlib import Path
from typing import Any

import tomlkit


class PyProjectParser:
    """Parse the pyproject.toml file in the current folder."""

    def __init__(self):
        """Initialize the PyProjectParser."""
        with open("pyproject.toml", "rb") as f:
            self._pyproject = tomlkit.load(f)
        self._project = self._pyproject["project"]

    @property
    def app_entry(self):
        return self._pyproject["tool"]["box"]["app_entry"]

    @property
    def builder(self) -> str:
        """Return the builder of the project."""
        return self._pyproject["tool"]["box"]["builder"]

    @property
    def name(self) -> str:
        """Return the name of the project."""
        return self._project["name"]

    @property
    def name_pkg(self) -> str:
        """Return the name of the package (project name with '-' replaced by '_')."""
        return self.name.replace("-", "_")

    @property
    def version(self) -> str:
        """Return the version of the project."""
        return self._project["version"]

    @property
    def scripts(self) -> dict:
        """Return the scripts of the project."""
        return self._project["scripts"]

    @property
    def rye(self) -> dict:
        """Return the rye configuration of the project."""
        return self._pyproject["tool"]["rye"]


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

    with open(pyproject_file, "w") as f:
        tomlkit.dump(doc, f)
