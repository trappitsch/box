=== "Linux"

    The created installer is an executable bash script
    that contains bash installation instructions as well as the binary.
    It can be run - like any other bash script - as following:

    ```
    ./projectname-v1.2.3-installer.sh
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

    CLI installers on Windows are currently not supported.

=== "macOS"

    CLI installers on macOS are currently not supported.
