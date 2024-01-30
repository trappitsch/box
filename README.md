# box

[![PyPI](https://img.shields.io/pypi/v/box.svg)](https://pypi.org/project/box/)
[![Changelog](https://img.shields.io/github/v/release/trappitsc/box?include_prereleases&label=changelog)](https://github.com/trappitsc/box/releases)
[![Tests](https://github.com/trappitsc/box/actions/workflows/test.yml/badge.svg)](https://github.com/trappitsc/box/actions/workflows/test.yml)

Automatic packaging and installers of your GUI with PyApp

## Installation

Install this tool using `pip`:

    pip install box

## Usage

For help, run:

    box --help

You can also use:

    python -m box --help

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd box
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
