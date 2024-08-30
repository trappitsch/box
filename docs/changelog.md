## v0.4.0

- Remove PyApp Variables from initialization and put them into their own command.

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
