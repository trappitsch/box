# Initialize a new project

from typing import List

import rich_click as click

import box.formatters as fmt
import box.utils as ut
from box.config import PyProjectParser, pyproject_writer
from box.packager import PackageApp


class InitializeProject:
    """Initialize a new project."""

    def __init__(
        self,
        quiet: bool = False,
        builder: str = None,
        optional_deps: str = None,
        is_gui: bool = None,
        app_entry: str = None,
        app_entry_type: str = None,
        python_version: str = None,
        opt_pyapp_vars: str = None,
    ):
        """Initialize the InitializeProject class.

        :param quiet: Flag to suppress output
        :param builder: Builder tool to use.
        :param optional_deps: Optional dependencies for the project.
        :param is_gui: Flag to set the project as a GUI project.
        :param app_entry: App entry for the project.
        :param app_entry_type: Entry type for the project in PyApp.
        :param python_version: Python version for the project.
        :param opt_pyapp_vars: Optional PyApp variables to set.
        """
        self._quiet = quiet
        self._builder = builder
        self._optional_deps = optional_deps
        self._is_gui = is_gui
        self._opt_paypp_vars = opt_pyapp_vars
        self._app_entry = app_entry
        self._app_entry_type = app_entry_type
        self._python_version = python_version

        self.app_entry = None
        self.pyproj = None

        self._set_pyproj()

    def initialize(self):
        """Initialize a new project.

        :param app_entry: the app entry point
        """
        self._set_builder()
        self._set_optional_deps()
        self._set_is_gui()
        self._set_app_entry()
        self._set_app_entry_type()
        self._set_python_version()

        if not self._quiet:
            fmt.success("Project initialized.")

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

        if self._app_entry:
            self.app_entry = self._app_entry
        else:
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

    def _set_app_entry_type(self):
        """Set the app entry type for the PyApp packaging. Defaults to `spec`."""
        default_entry_type = "spec"
        try:
            default_entry_type = self.pyproj.app_entry_type
        except KeyError:
            pass

        if self._app_entry_type:
            entry_type = self._app_entry_type.lower()
        else:
            if self._quiet:
                entry_type = default_entry_type
            else:
                entry_type = click.prompt(
                    "Choose an entry type for the project in PyApp.",
                    type=click.Choice(ut.PYAPP_APP_ENTRY_TYPES),
                    default=default_entry_type,
                )

        pyproject_writer("entry_type", entry_type)

    def _set_builder(self):
        """Set the builder for the project (defaults to rye)."""
        possible_builders = PackageApp().builders

        default_builder = "rye"
        try:
            default_builder = self.pyproj.builder
        except KeyError:
            pass

        if self._builder:
            builder = self._builder
        else:
            if self._quiet:
                builder = default_builder
            else:
                builder = click.prompt(
                    "Choose a builder tool for the project.",
                    type=click.Choice(possible_builders),
                    default=default_builder,
                )

        pyproject_writer("builder", builder)
        # reload
        self._set_pyproj()

    def _set_is_gui(self):
        """Set if the project is a GUI project or not."""
        if self._is_gui is not None:
            is_gui = self._is_gui
        else:
            if self._quiet:
                try:
                    is_gui = self.pyproj.is_gui
                except KeyError:
                    is_gui = False
            else:
                is_gui = click.confirm("Is this a GUI project?", default=False)

        pyproject_writer("is_gui", is_gui)

    def _set_optional_deps(self):
        """Set optional dependencies for the project (if any)."""
        if (tmp := self.pyproj.optional_dependencies) is not None:
            default_optional_deps = tmp
        else:
            default_optional_deps = ""

        if self._optional_deps:
            opt_deps = self._optional_deps
        else:
            if self._quiet:
                opt_deps = default_optional_deps
            else:
                opt_deps = click.prompt(
                    "Provide any optional dependencies for the project.",
                    type=str,
                    default=default_optional_deps,
                )

        if opt_deps != "":
            pyproject_writer("optional_deps", opt_deps)

    def _set_pyproj(self):
        """Check if the pyproject.toml file is valid."""
        try:
            self.pyproj = PyProjectParser()
        except KeyError:
            raise click.ClickException(
                "Invalid `pyproject.toml` file. Missing `project` table."
                "At least the `name` and `version` keys are required."
            )

    def _set_python_version(self):
        """Set the python version for the project.

        Ask the user what python version to use. If none is provided (or quiet),
        set the default to the latest python version.
        """
        if (tmp := self.pyproj.python_version) is not None:
            default_py_version = tmp
        else:
            default_py_version = ut.PYAPP_PYTHON_VERSIONS[-1]

        if self._python_version:
            py_version = self._python_version
        else:
            if self._quiet:
                py_version = default_py_version
            else:
                py_version = click.prompt(
                    "Choose a python version for packaging the project with PyApp.",
                    type=click.Choice(ut.PYAPP_PYTHON_VERSIONS),
                    default=default_py_version,
                )

        pyproject_writer("python_version", py_version)
