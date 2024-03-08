# Welcome to `box`

[![Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/mitsuhiko/rye/main/artwork/badge.json)](https://rye-up.com)
[![tests](https://github.com/trappitsch/box/actions/workflows/tests.yml/badge.svg)](https://github.com/trappitsch/box/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/trappitsch/box/graph/badge.svg?token=CED96ANLRR)](https://codecov.io/gh/trappitsch/box)

The goal of this package is
to provide a command line interface
that allows you to easily package your existing python project
with [`PyApp`](https://ofek.dev/pyapp/).

Currently, `box` only support python projects that have their metadata stored in a `pyproject.toml` file.
See [here](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml)
for details.

!!! warning
    This package is still in a very early
    development phase! Please report your findings and issues,
    so that we can improve this tool together.

## Pre-requisites

In order to run `box`, you must have `cargo` installed.
Instructions to do so can be found
[here](https://doc.rust-lang.org/cargo/getting-started/installation.html).


## Installation

!!! failure

    The installation from `pypi` (top part from given options below) is currently not available.
    If you want to test this project, please use the installation from github.

!!! abstract "Installation Instructions"

    {% include-markdown ".includes/install.md" %}


## Usage - the short version

### Initialize a project

From within your project directory, run:

```
box init
```

This will ask you a few questions, answer them, and you will be done.

### Packaging

To package your project, run:

```
box package
```

This will first build your project using. the selected builder.
Then, the latest `PyApp` source will be downloaded and unpacked.
Finally, the project will be packaged with `PyApp` using `cargo`.

You can find the executable in the `target/release` directory.

### Further resources

- [CLI overview documentation](cli.md)
- [Detailed usage guide](guide.md)
