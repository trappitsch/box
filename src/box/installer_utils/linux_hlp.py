# Helper functions to create a linux GUI installer.


def create_bash_installer_cli(name_pkg, version) -> str:
    """Create a bash installer for a CLI application.

    :param name_pkg: The name of the program.
    :param version: The version of the program.

    :return: The bash installer content.
    """
    return rf"""#!/bin/bash
# This is a generated installer for {name_pkg} v{version}

# Default installation name and folder
INSTALL_NAME={name_pkg}
INSTALL_DIR=/usr/local/bin

# Check if user has a better path:
read -p "Enter the installation path (default: $INSTALL_DIR): " USER_INSTALL_DIR
if [ ! -z "$USER_INSTALL_DIR" ]; then
    INSTALL_DIR=$USER_INSTALL_DIR
fi

# Check if installation folder exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: Installation folder does not exist."
    exit 1
fi

# Check if installation folder requires root access
if [ ! -w "$INSTALL_DIR" ]; then
    echo "Error: Installation folder requires root access. Please run with sudo."
    exit 1
fi

INSTALL_FILE=$INSTALL_DIR/$INSTALL_NAME

# check if installation file already exist and if it does, ask if overwrite is ok
if [ -f "$INSTALL_FILE" ]; then
    read -p "File already exists. Overwrite? (y/n): " OVERWRITE
    if [ "$OVERWRITE" != "y" ]; then
        echo "Installation aborted."
        exit 1
    fi
fi

if ! [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then\
  echo "$INSTALL_DIR is not on your PATH. Please add it."
fi


sed -e '1,/^#__PROGRAM_BINARY__$/d' "$0" > $INSTALL_FILE
chmod +x $INSTALL_FILE

echo "Successfully installed $INSTALL_NAME to $INSTALL_DIR"
exit 0
#__PROGRAM_BINARY__
"""


def create_bash_installer_gui(name_pkg, version, icon_name) -> str:
    """Create a bash installer for a GUI application.

    :param name_pkg: The name of the program.
    :param version: The version of the program.
    :param icon_name: The name of the icon file.

    :return: The bash installer content.
    """
    return rf"""#!/bin/bash
#
# This script is used to install {name_pkg}, {version}.

# Program specific variables
INSTALL_NAME={name_pkg}
ICON_NAME={icon_name}

# Default installation name and folder
INSTALL_DIR=$HOME/.local/share/$INSTALL_NAME
DESKTOP_DIR=$HOME/.local/share/applications

# Check if user has a better path:
read -p "Enter the installation path (absolute path) or press enter for using the default: $INSTALL_DIR): " USER_INSTALL_DIR
if [ ! -z "$USER_INSTALL_DIR" ]; then
    INSTALL_DIR=$USER_INSTALL_DIR
fi

# Check if user has a better Desktop path:
read -p "Enter the path for the desktop file or press enter for using the default: $DESKTOP_DIR): " USER_DESKTOP_DIR
if [ ! -z "$USER_DESKTOP_DIR" ]; then
    DESKTOP_DIR=$USER_DESKTOP_DIR
fi

# Check if installation folder exists
if [ -d "$INSTALL_DIR" ]; then
    # ask if installation folder should be used even though it exists
    read -p "Installation folder already exists. Continue? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Installation aborted."
        exit 1
    fi
else
    # create folder
    mkdir -p $INSTALL_DIR
fi

# Check if desktop file folder exists, if not throw an error
if [ ! -d "$DESKTOP_DIR" ]; then
    echo "Error: Desktop file folder does not exist. Please create it first or provide a valid path."
    exit 1
fi

# Check if installation folder requires root access
if [ ! -w "$INSTALL_DIR" ]; then
    echo "Error: Installation folder requires root access. Please run with sudo."
    exit 1
fi

# Check if desktop file folder requires root access
if [ ! -w "$DESKTOP_DIR" ]; then
    echo "Error: Desktop file folder requires root access. Please run with sudo."
    exit 1
fi

# Copy the binary and the icon to the installation folder


INSTALL_FILE=$INSTALL_DIR/$INSTALL_NAME
ICON_FILE=$INSTALL_DIR/$ICON_NAME
DESKTOP_FILE=$DESKTOP_DIR/$INSTALL_NAME.desktop

# check if installation file already exist and if it does, ask if overwrite is ok
if [ -f "$INSTALL_FILE" ]; then
    read -p "File already exists. Overwrite? (y/n): " OVERWRITE
    if [ "$OVERWRITE" != "y" ]; then
        echo "Installation aborted."
        exit 1
    fi
fi

# check if icon file already exist and if it does, ask if overwrite is ok
if [ -f "$ICON_FILE" ]; then
    read -p "Icon file already exists. Overwrite? (y/n): " OVERWRITE
    if [ "$OVERWRITE" != "y" ]; then
        echo "Installation aborted."
        exit 1
    fi
fi

# check if desktop file already exist and if it does, ask if overwrite is ok
if [ -f "$DESKTOP_FILE" ]; then
    read -p "Desktop file already exists. Overwrite? (y/n): " OVERWRITE
    if [ "$OVERWRITE" != "y" ]; then
        echo "Installation aborted."
        exit 1
    fi
fi

# do the copying
sed -n '/^#__PROGRAM_BINARY__$/,/^#__ICON_BINARY__$/p' < "$0" | sed '1d;$d' > $INSTALL_FILE
sed -e '1,/^#__ICON_BINARY__$/d' "$0" > $ICON_FILE

# make the installation file executable
chmod +x $INSTALL_FILE

# Create the desktop file
echo "[Desktop Entry]" > $DESKTOP_FILE
echo "Type=Application" >> $DESKTOP_FILE
echo "Name=$INSTALL_NAME" >> $DESKTOP_FILE
echo "Exec=$INSTALL_FILE" >> $DESKTOP_FILE
echo "Icon=$ICON_FILE" >> $DESKTOP_FILE
chmod +x $DESKTOP_FILE

# Finally, let's create a bash uninstaller script and make it executable
UNINSTALL_FILE=$INSTALL_DIR/uninstall_$INSTALL_NAME.sh
echo "#!/bin/bash" > $UNINSTALL_FILE
echo "" >> $UNINSTALL_FILE
echo "read -p \"This will delete the program folder, program data, and desktop integration file for $INSTALL_NAME. Continue? (y/n): \" CONTINUE" >> $UNINSTALL_FILE
echo "    if [ \"\$CONTINUE\" != \"y\" ]; then" >> $UNINSTALL_FILE
echo "        echo \"Uninstaller aborted.\"" >> $UNINSTALL_FILE
echo "        exit 1" >> $UNINSTALL_FILE
echo "    fi" >> $UNINSTALL_FILE
echo "" >> $UNINSTALL_FILE
echo "rm -f $INSTALL_DIR/$INSTALL_NAME" >> $UNINSTALL_FILE
echo "rm -f $INSTALL_DIR/$ICON_NAME" >> $UNINSTALL_FILE
echo "rm -f $UNINSTALL_FILE" >> $UNINSTALL_FILE
echo "rmdir $INSTALL_DIR" >> $UNINSTALL_FILE
echo "rm -f $DESKTOP_FILE" >> $UNINSTALL_FILE
echo "rm -rf $HOME/.local/share/pyapp/$INSTALL_NAME" >> $UNINSTALL_FILE
echo "" >> $UNINSTALL_FILE
echo "echo \"Successfully uninstalled $INSTALL_NAME.\"" >> $UNINSTALL_FILE
echo "exit 0" >> $UNINSTALL_FILE
chmod +x $UNINSTALL_FILE

# Notify user of successful installation
echo "Successfully installed $INSTALL_NAME to $INSTALL_DIR"
exit 0
#__PROGRAM_BINARY__
"""
