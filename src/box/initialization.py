# Initialize a new project

from typing import List

import rich_click as click

from box.config import PyProjectParser, pyproject_writer
import box.formatters as fmt
from box.packager import PackageApp


class InitializeProject:
    """Initialize a new project.

    # todo: allow for custom build command, custom dist folder
    """

    def __init__(self, quiet: bool = False):
        """Initialize the InitializeProject class.

        :param quiet: bool, flag to suppress output
        """
        self._quiet = quiet

        self.app_entry = None
        self.pyproj = None

        self._set_pyproj()

    def initialize(self):
        """Initialize a new project.

        :param app_entry: the app entry point
        """
        self._set_builder()
        self._set_optional_deps()
        self._set_app_entry()

        if not self._quiet:
            fmt.success("Project initialized.")

    def _set_builder(self):
        """Set the builder for the project (defaults to rye)."""
        possible_builders = PackageApp().builders.keys()
        if self._quiet:
            builder = "rye"
        else:
            builder = click.prompt(
                "Choose a builder tool for the project.",
                type=click.Choice(possible_builders),
                default="rye",
            )
        pyproject_writer("builder", builder)
        # reload
        self._set_pyproj()

    def _set_app_entry(self):
        """Set the app entry for the project."""
        possible_entries = self.pyproj.possible_app_entries
        # create a list of possible entries
        options = []
        sup_keys = possible_entries.keys()  # outside keys
        for sup_key in sup_keys:
            for _, value in possible_entries[sup_key].items():
                options.append(value)

        def query_app_entry(query_txt, opts: List) -> None:
            """Query the user for a string prompt and set class variable."""

            user_entry = click.prompt(query_txt, type=str)
            try:
                self.app_entry = opts[int(user_entry)]
            except ValueError:
                self.app_entry = user_entry
            except IndexError:
                fmt.warning("Invalid entry. Please try again.")
                query_app_entry(query_txt, opts)

        if self._quiet:  # all automatic
            if options == []:  # choose package_name:run and raise warning
                self.app_entry = f"{self.pyproj.name_pkg}:run"
                fmt.warning(f"No app entry found, using {self.app_entry}:run.")
            else:
                self.app_entry = options[0]
        else:
            if options == []:
                self.app_entry = click.prompt(
                    "No app entry found. Please set an app entry for the project."
                )
            else:
                query_text = (
                    "Please type an app entry for the project or choose one "
                    "from the list below:\n"
                )
                for it, option in enumerate(options):
                    query_text += f"    [{it}] {option}\n"

                query_app_entry(query_text, options)

        pyproject_writer("app_entry", self.app_entry)

    def _set_optional_deps(self):
        """Set optional dependencies for the project (if any)."""
        if self._quiet:
            opt_deps = ""
        else:
            opt_deps = click.prompt(
                "Provide any optional dependencies for the project.",
                type=str,
                default="",
            )
        if opt_deps != "":
            pyproject_writer("optional_deps", opt_deps)

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
