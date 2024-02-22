# box

[![Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/mitsuhiko/rye/main/artwork/badge.json)](https://rye-up.com)
[![tests](https://github.com/trappitsch/box/actions/workflows/tests.yml/badge.svg)](https://github.com/trappitsch/box/actions/workflows/tests.yml)

The goal of this package is
to provide a command line interface
that allows you to easily package your existing python project
with [`PyApp`](https://ofek.dev/pyapp/).

**Important:** This package is still in a very early
development phase! Please report your findings and issues,
so that we can improve this tool together.

## Pre-requisites

In order to run `box`, you must have `cargo` installed.
Instructions to do so can be found
[here](https://doc.rust-lang.org/cargo/getting-started/installation.html).

Furthermore, we currently only support `rye` build environments,
however, support for more builders is planned for the near future.

## Installation

Install this tool using `pipx`:

    pipx install git+https://github.com/trappitsch/box.git

## Usage

### Initialize a project

From within your project directory, run:

```
box init
```

The initialization will ask your for your script entry point.
We automatically read `[project.scripts]` and `[project.gui-scripts]`
to propose some values to select from.
However, you can also type your own entry point.
This is the entry point that will be set in `PyApp`
using the `PYAPP_EXEC_SPEC` environment variable.
Details can be found [here](https://ofek.dev/pyapp/latest/config/#execution-mode).

### Packaging

To package your project, run:

```
box package
```

This will first build your project using `rye`.
Then, the latest `PyApp` source will be downloaded and unpacked.
Finally, the project will be packaged with `PyApp` using `cargo`.

You can find the executable in the `target/release` directory.
