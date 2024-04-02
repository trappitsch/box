# Welcome to `box`

[![Docs](https://readthedocs.org/projects/box/badge/?version=latest)](https://box.readthedocs.io/en/latest/?badge=latest)
[![tests](https://github.com/trappitsch/box/actions/workflows/tests.yml/badge.svg)](https://github.com/trappitsch/box/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/trappitsch/box/graph/badge.svg?token=CED96ANLRR)](https://codecov.io/gh/trappitsch/box)
[![Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/mitsuhiko/rye/main/artwork/badge.json)](https://rye-up.com)

The goal of this package is
to provide a command line interface
that allows you to easily package your existing python project
with [`PyApp`](https://ofek.dev/pyapp/).

Currently, `box` only support python projects that have their metadata stored in a `pyproject.toml` file.
See [here](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml)
for details.

!!! warning
    - This package is still in a very early
    development phase! Please report your findings and issues,
    so that we can improve this tool together.
    - `box` is not yet production ready
    and breaking changes may occur with new releases.
    These will be noted in the release notes
    and in the [changelog](changelog.md).

## Issues, comments, contributions,...

We welcome contributions to this project.
If you run into any problem, want to suggest a feature, want to contribute, or just want to say hi,
please feel free to open an issue on [GitHub](https://github.com/trappitsch/box/issues)
or to start a new [discussion](https://github.com/trappitsch/box/discussions).

## Pre-requisites

In order to run `box`, you must have `cargo` installed.
Instructions to do so can be found
[here](https://doc.rust-lang.org/cargo/getting-started/installation.html).


## Installation

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
