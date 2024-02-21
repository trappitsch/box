"""Provide my own formatters for echoing, etc.

These methods are used to standardize the output of the CLI commands.
"""

import rich_click as click


def info(msg: str) -> None:
    """Echo an info message to the console.

    :param msg: Info message to print
    """
    click.secho(f"Info: {msg}", fg="blue")


def success(msg: str) -> None:
    """Echo a success message to the console.

    :param msg: Success message to print
    """
    click.secho(f"Success: {msg}", fg="green")


def warning(msg: str) -> None:
    """Echo a warning message to the console.

    :param msg: Warning message to print
    """
    click.secho(f"Warning: {msg}", fg="yellow")
