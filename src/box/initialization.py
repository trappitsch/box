# Initialize a new project


import click

from box.config import PyProjectParser, pyproject_writer


class InitializeProject:
    """Initialize a new project."""

    def __init__(self):
        """Initialize the InitializeProject class."""
        self.pyproj = None

        # set box variables
        self._set_pyproj()
        self._set_builder()
        self._set_app_entry()

    def initialize(self):
        """Initialize a new project."""
        click.echo("Project initialized.")

    def _set_builder(self):
        """Set the builder for the project."""
        try:
            _ = self.pyproj.rye
            pyproject_writer("builder", "rye")
        except KeyError:
            raise click.ClickException(
                "No builder tool was found in configuration. "
                "Currently only `rye` is supported."
            )
        # reload
        self._set_pyproj()

    def _set_app_entry(self):
        """Set the app entry for the project."""
        # todo: give options here
        # todo: if no options given, check existing ones and if only one, then use it
        pkg_name = self.pyproj.name_pkg
        pyproject_writer("app_entry", f"{pkg_name}:run")

    def _set_pyproj(self):
        """Check if the pyproject.toml file is valid."""
        try:
            self.pyproj = PyProjectParser()
        except FileNotFoundError:
            raise click.ClickException(
                "No `pyproject.toml` file found in current folder."
            )
        except KeyError:
            raise click.ClickException(
                "Invalid `pyproject.toml` file. Missing `project` table."
                "At least the `name` and `version` keys are required."
            )
