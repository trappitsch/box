# Helper functions to create a linux CLI installer.


def create_bash_installer(name_pkg, version) -> str:
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
