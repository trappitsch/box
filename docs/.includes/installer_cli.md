=== "Linux"

    The created installer is an executable bash script
    that contains bash installation instructions as well as the binary.
    It can be run - like any other bash script - as following:

    ```
    ./projectname-v1.2.3-linux.sh
    ```

    The installer will ask the user for the target directory (defaults to `/usr/local/bin`)
    and copy the CLI binary there under the name `projectname`.
    It will also make the copied binary executable.

    The installer script has a few checks to ensure that the installation is successful:

    - It checks if the target directory exists, if not throws an error.
    - It checks if the target directory is writable, if not, tells the user to run the installer with `sudo`.
    - It checks if the binary already exists in the target directory, if so asks the user if it should overwrite it or not and proceeds accordingly.
    - It checks if the install directory is on the `PATH` and if not, tells the user to add it.

    The binary itself is included in the installer script below the line marked with
    `#__PROGRAM_BINARY__`.

=== "Windows"

    Windows installers are created using
    [NSIS](https://nsis.sourceforge.io/Main_Page).
    You must ensure that NSIS is installed and available on the system path.
    The installer is an executable in `target/release/projectname-v1.2.3-win.exe`
    that can be run by double-clicking it.

    The installer will ask the user for the target directory.
    It will then copy the binary to the target directory and create an uninstaller.

    When using the uninstaller that is created with NSIS, all PyApp data from this project will be removed as well in order to provide the user with a clean uninstallation.

    !!! warning
        The installer will not add the install directory to the `PATH` variable.
        You or the user must do this manually.
        This is also stated on the last page of the installer.

=== "macOS"

    MacOS CLI tool installers are created using
    [applecrate](https://github.com/RhetTbull/applecrate).
    The installer is an executable in
    `target/release/projectname-v1.2.3-macos.pkg`
    that can be run by double-clicking it.

    !!! bug
        The uninstaller does currently not remove the virtual environment
        that is created by PyApp, but only removes the executable.
        This will be fixed in a future release.
