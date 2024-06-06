=== "Linux"

    The created installer is an executable bash script
    that contains bash installation instructions,
    the binary program,
    and the program icon.
    It can be run - like any other bash script - as following:

    ```
    ./projectname-v1.2.3-linux.sh
    ```

    The installer will ask the user for the target directory
    (defaults to `$HOME/.local/share/projectname`)
    and the path to copy the `.desktop` file to
    (defaults to `$HOME/.local/share/applications`).

    The installer will copy the binary and the icon to the target directory,
    will create an uninstaller bash script in the target directory,
    and create a `.desktop` file in the specified path.
    It will also make the copied binary, desktop file, and uninstaller executable.

    The installer script has a few checks to ensure that the installation is successful:

    - It checks if the target directory exists.
      If it exists, the script will check with the user if it should continue,
      otherwise it will create the folder.
    - It checks if the target and desktop file directories are ritable, if not, tells the user to run the installer with `sudo`.
    - It checks if the files already exists in the target directory, if so asks the user if it should overwrite it or not and proceeds accordingly.

    The binary itself is included in the installer script below the line marked with
    `#__PROGRAM_BINARY__` and before the line marked with `#__ICON_BINARY__`.
    The icon itself is included in the installer script below the line marked with
    `#__ICON_BINARY__`.
    The uninstaller is created from within the bash script itself.


=== "Windows"

    Windows installers are created using
    [NSIS](https://nsis.sourceforge.io/Main_Page).
    You must ensure that NSIS is installed and available on the system path.
    The installer is an executable in `target/release/projectname-v1.2.3-win.exe`
    that can be run by double-clicking it.

    The installer will ask the user for the target directory and if
    a startmenu entry should be created.
    It will then create the startmenu entry and copy the binary to the target directory. An uninstaller is created as well.

    When using the uninstaller that is created with NSIS, all PyApp data from this project will be removed as well in order to provide the user with a clean uninstallation.

=== "macOS"

    A MacOS GUI is created by manually first putting together
    a minimal `.app` directory structure.
    This directory contains the binary, the icon, and a `Info.plist` file.

    A `.dmg` file is then created using
    [dmgbuild](https://github.com/dmgbuild/dmgbuild).

    !!! note
        The building process of the `.dmg` file can currently not yet
        be customized.
        We are using some default settings, however,
        hopefully in the future we can make this more customizable.

    In order for this to work, you must have an `icon.icns` file
    in the `assets` folder of your project directory.
