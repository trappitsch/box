# Helper functions to create Mac Installers

import shutil
from pathlib import Path


def dmgbuild_settings(target_path: Path, name_pkg: str, icon: Path) -> dict:
    """Create the settings for building the dmg file.

    :param target_path: Path to the target folder, i.e., where the app is and where the dmg will be created.
    :param name_pkg: The name of the package as a string, same name as the app (but without the `.app`)!
    :param icon: Path to the icon file.
    """
    settings = {
        "files": [str(target_path.joinpath(name_pkg).with_suffix(".app").absolute())],
        "symlinks": {"Applications": "/Applications"},
        "icon_locations": {f"{name_pkg}.app": (140, 120), "Applications": (500, 120)},
        "background": "builtin-arrow",
    }

    return settings


def make_app(
    target_path: Path, name_pkg: str, author: str, version: str, icon: Path
) -> None:
    """Create an apple executable `.app` file.

    Creates the folder structure and `Info.plist` file required for an `.app` Apple App.

    :param target_path: Path to the target folder, i.e., where the binary is and where the app will be created.
    :param name_pkg: The name of the package as a string, same name as the binary!
    :param version: Version of the package, as string, `X.Y.Z`.
    :param icon: Path to the icon `.icns` file.
    """
    app_path = target_path.joinpath(name_pkg).with_suffix(".app")
    app_path.mkdir()

    # create resource directory and copy icon into it
    res_path = app_path.joinpath("Contents/Resources")
    res_path.mkdir(parents=True)
    shutil.copy(icon, res_path.joinpath(icon.name))

    # create MacOS directory and copy binary into it
    macos_path = app_path.joinpath("Contents/MacOS")
    macos_path.mkdir(parents=True)
    shutil.copy(target_path.joinpath(name_pkg), macos_path.joinpath(name_pkg))

    # Create the Info.plist file
    name_pkg_short = name_pkg if len(name_pkg) <= 16 else name_pkg[:16]
    info_plist = rf"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIdentifier</key>
    <string>com.box-package.{name_pkg}</string>
    <key>CFBundleExecutable</key>
    <string>{name_pkg}</string>
    <key>CFBundleIconFile</key>
    <string>{icon.name}</string>
    <key>CFBundleDisplayName</key>
    <string>{name_pkg}</string>
    <key>CFBundleName</key>
    <string>{name_pkg_short}</string>
    <key>CFBundleVersion</key>
    <string>{version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{version}</string>
    <key>NSHumanReadableCopyright</key>
    <string>{author}</string>
    <key>CFBundleSignature</key>
    <string>????</string>
</dict>
</plist>"""

    info_plist_file = app_path.joinpath("Contents/Info.plist")
    with open(info_plist_file, "w") as f:
        f.write(info_plist)
