"""Provide my own formatters for echoing, etc.

These methods are used to standardize the output of the CLI commands.
"""

import rich_click as click


def info(msg: str, **kwargs) -> None:
    """Echo an info message to the console.

    :param msg: Info message to print
    :param kwargs: Additional keyword arguments for `click.secho`
    """
    click.secho(f"Info: {msg}", fg="cyan", **kwargs)


def success(msg: str, **kwargs) -> None:
    """Echo a success message to the console.

    :param msg: Success message to print
    :param kwargs: Additional keyword arguments for `click.secho`
    """
    click.secho(f"Success: {msg}", fg="green", **kwargs)


def warning(msg: str, **kwargs) -> None:
    """Echo a warning message to the console.

    :param msg: Warning message to print
    :param kwargs: Additional keyword arguments for `click.secho`
    """
    click.secho(f"Warning: {msg}", fg="yellow", **kwargs)
