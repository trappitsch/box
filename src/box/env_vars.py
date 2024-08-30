# Deal with environmental variables.

from enum import Enum

import rich_click as click
from rich_click import ClickException

import box.config as cfg
import box.formatters as fmt


class VariableType(Enum):
    """Define valid variable types that can be set."""

    STRING = "string"  # default
    INT = "int"
    BOOL = "bool"


def get_list() -> None:
    """Get a list of all environmental variables set in the configuration."""
    parser = cfg.PyProjectParser()
    env_vars = parser.env_vars

    if not env_vars:
        fmt.warning("No variables set.")
    else:
        for key, value in env_vars.items():
            click.secho(f"{key}: {value}")


def get_var(name: str) -> None:
    """Get a variable name and display its name."""
    parser = cfg.PyProjectParser()
    env_vars = parser.env_vars

    try:
        click.secho(env_vars[name])
    except KeyError:
        fmt.warning(f"No variable named {name} found in the configuration.")


def set_bool(key_val: str) -> None:
    """Set a key-value pair as a boolean.

    :param key_val: Key-value pair to set environmental variable to, as an boolean.
    """
    typ = VariableType.BOOL
    _set_variable(key_val, typ)


def set_int(key_val: str) -> None:
    """Set a key-value pair as a integer.

    :param key_val: Key-value pair to set environmental variable to, as an integer.
    """
    typ = VariableType.INT
    _set_variable(key_val, typ)


def set_string(key_val: str) -> None:
    """Set a key-value pair as a string.

    :param key_val: Key-value pair to set environmental variable to, as a string.
    """
    typ = VariableType.STRING
    _set_variable(key_val, typ)


def unset(var: str) -> None:
    """Unset a variable.

    If set, will print a success message, otherwise a warning that variable
    could not be found.

    :param var: Variable name.
    """
    status = cfg.unset_env_variable(var)
    if status:
        fmt.success(f"Variable {var} unset.")
    else:
        fmt.warning(f"Could not find variable {var}.")


def _check_bool(val: str) -> bool:
    """Check an input string to see if it contains a boolean value.

    Valid strings are:
    - True: "1", "True" (case insensitive)
    - False: "0", "False" (case insensitive)

    :param val: Value as a string.

    :return: Boolean value of the input string.

    :raises: ClickException if none of these values were given.
    """
    if val == "1" or val.lower() == "true":
        return True
    elif val == "0" or val.lower() == "false":
        return False
    else:
        raise ClickException(f"Cannot convert {val} to a boolean.")


def _set_variable(key_val: str, typ: VariableType) -> None:
    """Set a key-value pair with a given type for the type.

    If the key-value pair is invalid, the CLI will return an error saying so.
    Otherwise, the variable will be written to `pyproject.toml`.
    Already existing values will simply be overwritten.

    :param key_val: Key-value pair to set.
    :param typ: Type to set it too.
    """
    key_val = key_val.split("=")
    if len(key_val) != 2:
        raise ClickException("Variables to set must be a key-value pair")

    if typ == VariableType.STRING:
        key = key_val[0]
        value = key_val[1]
    elif typ == VariableType.INT:
        key = key_val[0]
        try:
            value = int(key_val[1])
        except Exception as e:
            raise ClickException(
                f"Problem converting {key_val[1]} to an integer"
            ) from e
    elif typ == VariableType.BOOL:
        key = key_val[0]
        value = _check_bool(key_val[1])

    cfg.pyproject_writer(key, value, category="env-vars")

    fmt.success(f"Variable {key} successfully set to {value} (type {typ.value}).")
