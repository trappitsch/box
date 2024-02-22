# Build the `qtcowsay` project with PyApp.

from pathlib import Path

from click.testing import CliRunner
from git import Repo
import pytest

from box.cli import cli


GIT_URL = "https://github.com/trappitsch/qtcowsay.git"  # repo for qtcowsay


@pytest.mark.unit
def test_gui_build():
    """Build the `qtcowsay` project with PyApp."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # app expected
        app_expected = Path("target/release/qtcowsay")

        # clone the repo
        Repo.clone_from(GIT_URL, ".")

        # init and build
        runner.invoke(cli, ["init", "-q"])
        result = runner.invoke(cli, ["package"])

        # check result
        assert result.exit_code == 0
        assert "Project successfully packaged" in result.output
        assert app_expected.exists()
