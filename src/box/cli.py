import click

from box.cleaner import CleanProject
from box.initialization import InitializeProject
from box.packager import PackageApp


@click.group()
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
def init(quiet):
    """Initialize a new project in the current folder."""
    my_init = InitializeProject(quiet=quiet)

    # if not quiet, prompt for values
    if not quiet:
        name_default = my_init.pyproj.name
        name = click.prompt("Enter project name", default=name_default)
    my_init.initialize()


@cli.command(name="package")
def package():
    """Build the project, then package it with PyApp."""
    my_packager = PackageApp()
    my_packager.build()
    my_packager.package()
    click.echo(
        "Project successfully packaged. "
        "You can find the binary file in the `target/release` folder."
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
    my_cleaner = CleanProject(
        dist=dist,
        build=build,
        target=target,
        source_pyapp=source_pyapp,
        pyapp_folder=pyapp_folder,
    )
    my_cleaner.clean()
