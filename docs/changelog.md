- Released binary is now named after the project name, not after the python package name
- Add command `box installer` to create an installer for the packaged program.
    - CLI on Linux: Install via a `bash` script with embedded binary.
    - GUI on Linux: Install via a `bash` script with embedded binary and icon.
    - CLI on Windows: Installer created using [NSIS](https://nsis.sourceforge.io/Main_Page).
    - GUI on Windows: Installer created using [NSIS](https://nsis.sourceforge.io/Main_Page).
- Improvements to packaging: If PyApp fails and no binary exists, are more useful error message is provided.

## v0.1.0

First release of `box`.
