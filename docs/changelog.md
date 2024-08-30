## v0.4.0

**If you are setting PyApp variables, this is a breaking change!**

- Move environmental variables to their own table in `pyproject.toml`. They are now in `[tool.box.env-vars]`.
- Remove PyApp Variables from initialization and put them into their own command.
- Add a new command `box env` in order to manage environmental variables.
  - Add `box env --set KEY=VALUE` to add string variables.
  - Add `box env --set-int KEY=VALUE` to add integer variables.
  - Add `box env --set-bool KEY=VALUE` to add boolean variables.
  - Add `box env --get VAR_NAME` to get the value of a variable.
  - Add `box env --unset VAR_NAME` to remove a variable.
  - Add `box env --list` to list all variables.
- Bug fix for `box uninit`: Will throw a useful error if not in a `box` project.

If this breaks your project, you can either run `box uninit` followed by `box init` and re-enter the variables, or you can manually edit the `pyproject.toml` file.

## v0.3.0

- Fix linux GUI uninstaller, such that it will only delete the installation folder if it is empty.
- Allow icons to be stored in any folder that is named `assets`.
- Finish installers for MacOS.
    - CLI installer is created using [applecrate](https://github.com/RhetTbull/applecrate) and standard configuration.
    - GUI installer is created by creating a minimal folder structure for an `.app` file, packing the executable and the icon into it, and then creating a `.dmg` file using [`dmgbuild`](https://github.com/dmgbuild/dmgbuild) (with standard configuration).

## v0.2.0

- Released binary is now named after the project name, not after the python package name
- Improvements to packaging: If PyApp fails and no binary exists, are more useful error message is provided.
- Add command `box installer` to create an installer for the packaged program.
    - CLI on Linux: Install via a `bash` script with embedded binary.
    - GUI on Linux: Install via a `bash` script with embedded binary and icon.
    - CLI on Windows: Installer created using [NSIS](https://nsis.sourceforge.io/Main_Page).
    - GUI on Windows: Installer created using [NSIS](https://nsis.sourceforge.io/Main_Page).

## v0.1.0

First release of `box`.
