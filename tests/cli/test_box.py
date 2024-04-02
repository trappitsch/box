# General tests for CLI

import importlib.metadata

from click.testing import CliRunner

from box.cli import cli


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")
        assert result.output.rstrip().endswith(
            importlib.metadata.version("box_packager")
        )
