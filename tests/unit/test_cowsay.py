# Build the `cowsay` project with PyApp.

import os
from pathlib import Path

from click.testing import CliRunner
from git import Repo
import pytest

from box.cli import cli


GIT_URL = "https://github.com/VaasuDevanS/cowsay-python.git"  # repo for qtcowsay
COMMIT_HASH = "9b627e154adb29f3840a0f92229b88fbd495baf4"  # commit hash for v6.1


@pytest.mark.unit
def test_gui_build():
    """Build the `qtcowsay` project with PyApp."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # app expected
        app_expected = Path("target/release/cowsay")
        if os.name == "nt":  # on windows with have an .exe!
            app_expected = app_expected.with_suffix(".exe")

        # clone the repo
        repo = Repo.clone_from(GIT_URL, ".")
        repo.git.checkout(COMMIT_HASH)  # prevent repo-jacking

        # init and build
        runner.invoke(cli, ["init", "-q", "-b", "build"])
        result = runner.invoke(cli, ["package"])

        # check result
        assert result.exit_code == 0
        assert "Project successfully packaged" in result.output
        assert app_expected.exists()
