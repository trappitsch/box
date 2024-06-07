# Tips and Tricks for using `box`

## GUI programs and icons

### Icon files

With GUI programs, you will want to provide an icon file.
This icon file should be in a directory named `assets`.
The location of the `assets` directory is not important, but must be inside the project.
The icon itself must be named `icon.EXT`, where `EXT` is the file extension of the icon file.

Different icon files are required for different platforms.

- **Linux**: The icon file should be a `.svg` or `.png` file.
- **Windows**: The icon file should be a `.ico` file. There are many online converters that work reasonably well to turn `.svg` or `.png` files into `.ico` files.
- **MacOS**: The icon file should be a `.icns` file. If you create these on Linux, you might want to check [this article](https://dentrassi.de/2014/02/25/creating-mac-os-x-icons-icns-on-linux/) on how to create them.

### Associating your icon with your GUIk

THe installer itself will only associate the icon with the executable but NOT with your GUI.
Basically, the executable is a python shell that will run your GUI program and then detach from it.
Thus, the actual GUI program and the executable that your user will get are different.

!!! tip

    You should point this out to your user, since it can be confusing.
    For example, start menu / dock pinning on Windows and MacOS will only work with the executable,
    but not with the GUI program itself.
    This will be slightly confusing when executing the program, since the program will not be associated with
    the pinned start menu.
    If you have an idea how to fix this, please let me know!

If you are using `PyQt` or `PySide`,
you can associate the icon with the GUI program in the Main Window class.
Let's assume the following file tree:

```plaintext
|- src
|  |- pkg_name
|  |  |- __init__.py
|  |  |- main.py
|  |  |- assets
|  |  |  |- __init__.py
|  |  |  |- icon.svg
```

Here, we have the `assets` folder along with the source,
we put an `__init__`.py in there in order to ensure that it's added to the package.
In the `main.py` file, you can then associate the icon with the GUI program like this:

```python
from pathlib import Path

from qtpy import QtWidgets, QtGui

class MyProgram(QtWidgets.QMainWindow):
    """Main window of your program."""

    def __init__(self):
        super().__init__()

        icon = Path(__file__).parent.joinpath("assets/icon.svg").absolute()
        self.setWindowIcon(QtGui.QIcon(str(icon)))
```

This will associate the icon with the GUI program,
and the icon will be shown in the window title bar and in the task bar.
