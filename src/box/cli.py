import click

from box.initialization import InitializeProject
from box.packager import PackageApp


@click.group()
@click.version_option()
def cli():
    """Automatic packaging and installers of your GUI with PyApp."""
    pass


@cli.command(name="init")
@click.option(
    "-o",
    "--option",
    help="An example option",
)
def initialize(option):
    """Initialize a new project in the current folder."""
    my_init = InitializeProject()
    my_init.initialize()


@cli.command(name="package")
def build():
    """Package the project."""
    my_packager = PackageApp()
    my_packager.build()
    # todo add more info on where to find it
    click.echo("Project successfully packaged.")
