"""CLI for box-packager."""

from pathlib import Path

import rich_click as click

import box
import box.formatters as fmt
import box.utils as ut
from box import env_vars
from box.cleaner import CleanProject
from box.config import uninitialize
from box.initialization import InitializeProject
from box.installer import CreateInstaller
from box.packager import PackageApp

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(package_name="box_packager")
def cli():
    """Automatic packaging and installers of your GUI with PyApp."""
    pass


@cli.command(name="init")
@click.option(
    "-q",
    "--quiet",
    default=False,
    is_flag=True,
    help="Quiet mode: don't ask questions and initialize with default values.",
)
@click.option(
    "-b",
    "--builder",
    type=click.Choice(PackageApp().builders),
    help="Set the builder for the project.",
)
@click.option(
    "-opt", "--optional-deps", help="Set optional dependencies for the project."
)
@click.option(
    "--gui",
    is_flag=True,
    default=None,
    help=(
        "Set the project as a GUI project. In quiet mode, this will default to `False`."
    ),
)
@click.option("-e", "--entry", help="Set the app entry for the project.")
@click.option(
    "-et",
    "--entry-type",
    help=(
        "Set the app entry type (X) to pass to PyApp (`PYAPP_ENTRY_X`) for the project."
    ),
    type=click.Choice(ut.PYAPP_APP_ENTRY_TYPES),
)
@click.option(
    "-py",
    "--python-version",
    type=click.Choice(ut.PYAPP_PYTHON_VERSIONS),
    help="Set the python version to use with PyApp.",
)
def init(
    quiet,
    builder,
    optional_deps,
    gui,
    entry,
    entry_type,
    python_version,
):
    """Initialize a new project in the current folder."""
    ut.check_pyproject()
    my_init = InitializeProject(
        quiet=quiet,
        builder=builder,
        optional_deps=optional_deps,
        is_gui=gui,
        app_entry=entry,
        app_entry_type=entry_type,
        python_version=python_version,
    )
    my_init.initialize()


@cli.command(name="env")
@click.option(
    "--get", "get_var", help="Get the value that is currently set to a variable."
)
@click.option("--list", "list_vars", is_flag=True, help="List all variables set.")
@click.option(
    "--set",
    "set_string",
    help=("Set a `key=value` environmental variable pair with a string value."),
)
@click.option(
    "--set-bool",
    help=(
        "Set a `key=value` environmental variable pair with a boolean. "
        "Valid boolean values are `0`, `1`, `True`, `False` (case insensitive)."
    ),
)
@click.option(
    "--set-int",
    help=("Set a `key=value` environmental variable pair with an integer value."),
)
@click.option("--unset", help="Unset variable with a given name.")
def env(get_var, list_vars, set_bool, set_int, set_string, unset):
    """Manage the environmental variables.

    All environmental variables will be set when packaging the app with PyApp.
    Therefore, if you want to set specific PYAPP_X variables, set them here.
    """
    ut.check_boxproject()

    if get_var:
        env_vars.get_var(get_var)
    if set_bool:
        env_vars.set_bool(set_bool)
    if set_int:
        env_vars.set_int(set_int)
    if set_string:
        env_vars.set_string(set_string)
    if unset:
        env_vars.unset(unset)
    if list_vars:
        env_vars.get_list()


@cli.command(name="package")
@click.option(
    "-v",
    "--verbose",
    default=False,
    is_flag=True,
    help="Flag to enable verbose mode.",
)
@click.option(
    "-p",
    "--pyapp-source",
    default=None,
    help=(
        "Use local PyApp source code. "
        "Provide path to the folder or the .tar.gz archive."
    ),
)
@click.option(
    "-pv",
    "--pyapp-version",
    default="latest",
    help="Specify the PyApp version to use. See release page on PyApp GitHub.",
)
def package(verbose, pyapp_source, pyapp_version):
    """Build the project, then package it with PyApp.

    Note that if the pyapp source is already in the `build` directory,
    it will not be downloaded and/or extracted again.
    This speeds up the process if you are packaging multiple times.
    If you want to re-download it, please clean the project first with `box clean`.
    """
    ut.check_boxproject()
    my_packager = PackageApp(verbose=verbose)
    my_packager.check_requirements()
    my_packager.build()
    my_packager.package(pyapp_version, local_source=pyapp_source)
    binary_file = my_packager.binary_name
    fmt.success(
        f"Project successfully packaged.\n"
        f"You can find the executable file {binary_file.name} "
        f"in the `target/release` folder."
    )


@cli.command(name="installer")
@click.option(
    "-v",
    "--verbose",
    default=False,
    is_flag=True,
    help="Flag to enable verbose mode.",
)
def installer(verbose):
    """Create an installer for the project."""
    ut.check_boxproject()
    my_installer = CreateInstaller(verbose=verbose)
    my_installer.create_installer()
    inst_name = my_installer.installer_name
    if inst_name is not None:
        if Path(box.RELEASE_DIR_NAME).joinpath(inst_name).exists():
            fmt.success(
                f"Installer successfully created.\n"
                f"You can find the installer file {inst_name} "
                f"in the `target/release` folder."
            )
        else:
            raise click.ClickException(
                "Installer was not created. "
                "Run with `box installer -v` to get verbose feedback."
            )


@cli.command(name="clean")
@click.option(
    "-d",
    "--dist",
    default=False,
    is_flag=True,
    help="Flag to clean the `dist` folder where the python build lives.",
)
@click.option(
    "-b",
    "--build",
    default=False,
    is_flag=True,
    help="Flag to clean the `build` folder where the pyapp build lives.",
)
@click.option(
    "-t",
    "--target",
    default=False,
    is_flag=True,
    help="Flag to clean the `target` folder where the releases live.",
)
@click.option(
    "-s",
    "--source-pyapp",
    "source_pyapp",
    default=False,
    is_flag=True,
    help="Flag to clean the `pyapp-source.tar.gz` file. "
    "If set, `-b`, `--build` flag is ignored.",
)
@click.option(
    "-p",
    "--pyapp-folder",
    "pyapp_folder",
    default=False,
    is_flag=True,
    help="Flag to clean the `pyapp` folder(s) in `build`. "
    "If set, `-b`, `--build` flag is ignored.",
)
def clean(dist, build, target, source_pyapp, pyapp_folder):
    """Clean the whole project.

    By default, the `dist`, `build`, and `target` folders are deleted.
    The cleaner will ensure that you are in an initialized `box` project folder.
    """
    ut.check_boxproject()
    my_cleaner = CleanProject(
        dist=dist,
        build=build,
        target=target,
        source_pyapp=source_pyapp,
        pyapp_folder=pyapp_folder,
    )
    my_cleaner.clean()


@cli.command(name="uninit")
@click.option(
    "-c",
    "--clean-project",
    default=False,
    is_flag=True,
    help="Flag to clean the full project before uninitializing it.",
)
def uninit(clean_project):
    """Uninitialize the project.

    All references to `box` will be removed from the `pyproject.toml` file.
    """
    ut.check_boxproject()
    if clean_project:
        clean()
    uninitialize()
    fmt.success("Project un-initialized.")
