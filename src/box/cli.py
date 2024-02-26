import rich_click as click

from box.cleaner import CleanProject
from box.initialization import InitializeProject
import box.formatters as fmt
from box.packager import PackageApp
import box.utils as ut

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
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
@click.option("-e", "--entry", help="Set the app entry for the project.")
@click.option(
    "-py",
    "--python-version",
    type=click.Choice(ut.PYAPP_PYTHON_VERSIONS),
    help="Set the python version to use with PyApp.",
)
def init(quiet, builder, optional_deps, entry, python_version):
    """Initialize a new project in the current folder."""
    ut.check_pyproject()
    my_init = InitializeProject(
        quiet=quiet,
        builder=builder,
        optional_deps=optional_deps,
        app_entry=entry,
        python_version=python_version,
    )
    my_init.initialize()


@cli.command(name="package")
@click.option(
    "-v",
    "--verbose",
    default=False,
    is_flag=True,
    help="Flag to enable verbose mode.",
)
def package(verbose):
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
    my_packager.package()
    binary_file = my_packager.binary_name
    fmt.success(
        f"Project successfully packaged.\n"
        f"You can find the executable file {binary_file.name} in the `target/release` folder."
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
