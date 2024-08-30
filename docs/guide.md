# Detailed usage guide for `box`

Below are some detailed information on how to use `box`.
Note that you can always get help by typing `box -h` on the command line,
or by typing `box COMMAND -h` to obtain help for a specific command.

## Initialization

After you have installed `box`, navigate to the folder of your project.
Then, type

```
box init
```

This will start the initialization process of your project.
The initialization will ask you questions, unless the `-q`/`--quiet` flag is set.
If this flag is set, default values or user provided arguments will be used.

The following table shows a list of questions, their default values, their arguments to provide answers in quiet mode, and an explanation:

| Question                                                                   | Default                                                                                                                                                                                    | Argument                         | Explanation                                                                                                                                                                                                                                                                                                                                               |
|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Choose a builder tool for the project                                      | `rye`                                                                                                                                                                                      | `-b`<br> `--builder`             | *Required:* The builder to use to package your pyproject file. Valid tools are `rye`, `hatch`, `pdm`, `build`, and `flit`. Ensure that the builder is available in the environment in which you run box.                                                                                                                                                  |
| Provide any optional dependencies for the project.                         | `None`                                                                                                                                                                                     | `--opt`<br>`--optional-deps`     | *Optional:* Set any optional dependencies for the project. These are the dependencies that you would install in square brackets, e.g., via `pip install package_name[optional]`. If there are no optional dependencies, just hit enter.                                                                                                                   |
| Is this a GUI project?                                                     | `False`                                                                                                                                                                                    | `--gui` flag to toggle to `True` | Packaging a GUI project and a CLI project take place slightly differently in PyApp. If you package a GUI project without setting this option, a console will be shown in Windows and macos along with your GUI.                                                                                                                                           |                                                                                                                                          |
| Please type an app entry for the project or choose one from the list below | First entry in `pyproject.toml` for `[project.gui-scripts]`, if not available, then for `[project.scripts]`. If no entry points are given, the default value is set to `package_name:run`. | `-e`<br>`--entry`                | *Required:* The entry point for the application. This is the command that will be used to start the application. If you have a `pyproject.toml` file, `box` will try and read potential entry points that you can select by passing it the digit of the list. You can also provide an entry point manually by typing it here.                             |
| Choose an entry type for the project.                                      | `spec`                                                                                                                                                                                     | `-et`<br>`--entry-type`          | *Required:* This specifies the type of the entry point that `PyApp` will use. `spec` (default) is an object reference, `module` for a python module, `script` for a python script, and `notebook` for a jupyter notebook. Details can be found [here](https://ofek.dev/pyapp/latest/config/#execution-mode).                                              |
| Choose a python version to package the project with.                       | `3.12`                                                                                                                                                                                     | `--py`<br>`--python-version`     | *Required:* The python version to package with your project. You can choose any python version from the list. More details can be found on the `PyApp` website [here](https://ofek.dev/pyapp/latest/config/#python-distribution).                                                                                                                         |

If you provided all the answers, your project should have been successfully initialized and print an according message.

!!! tip
    While the recommended way to initialize a `box` project is simply to go through the questions that are asked
    during a `box init`, you can go through initialization in `-q`/`--quiet` mode.
    To still specify variables, just set them using the arguments discussed in the table above.
    And if you are happy with all the defaults, you should be good to do.

!!! note
    If you re-initalize a project, `box` will use the already set values as proposed default values.
    If you re-initialize in quiet mode and just give one new option, all other options will stay the same.

## Manage environmental variables

PyApp uses environmental variables for all configurations.
While `box` includes the basics of PyApp configuration,
you might want to set additional environmental variables.
This is done with the `box env` command.

### Set an environmental variable

You can set three types of environmental variables:

- `--set KEY=VALUE` to set a string variable.
- `--set-int KEY=VALUE` to set an integer variable.
- `--set-bool KEY=VALUE` to set a boolean variable.

For example, to set a string variable `MY_VAR` to `my_value`, type:

```
box env --set MY_VAR=my_value
```

### Get an environmental variable

Once set, you can simply get an environmental variable by typing:

```
box env --get VARIABLE_NAME
```

If not variable with this name is defined, a warning will be printed.
To list all currently set variables, type:

```
box env --list
```

### Unset a variable

To unset a variable, type:

```
box env --unset VARIABLE_NAME
```

## Packaging

To package your project, simply run:

```
box package
```

For verbose packaging, add the flag `-v` or `--verbose`.

This will take a bit of time and no output from building / packaging will be printed in non-verbose mode.
The following steps will be executed:

1. The project will be built using the selected builder.
2. The latest `PyApp` source will be downloaded and unpacked from GitHub.
3. The project will be packaged with `PyApp` using `cargo`.
4. The executable will be placed in the `target/release` directory and renamed to your package name.


!!! abstract "Building the python project"

    The python project will be built using the following command:

    {% include-markdown ".includes/build.md" %}

    This will put tye `.tar.gz` file of your project, which will then be packaged with `PyApp` into the `dist` folder.

### Specify `PyApp` version

If you would like to use a specific version of `PyApp` to package with,
you can provide the version number with the `-pv`/`--pyapp-version` argument.
Make sure that the version number corresponds to the correct tag on the
[GitHub release page of PyApp](https://github.com/ofek/pyapp/releases).

!!! note
    If you have a newer version of `PyApp` already downloaded,
    make sure to clean the project first with `box clean`.

### Local `PyApp` source

If you would like to provide a local `PyApp` source,
you can do so by providing either the path to the local `.tar.gz` source
or to a local folder using the `-p`/`--pyapp-source` argument.
The local source will then be used instead of the latest release from GitHub.
It will be copied into the `build` folder before packaging in the `pyapp-local` folder.
Running only `box package` when a local folder is present will always use this local folder
and not download any releases.
An information about this will be printed.

To re-copy the local source into the `build` folder,
the `box` project needs to be cleaned first.
Then run `box package -p LOCAL_SOURCE` again,
where `LOCAL_SOURCE` is the path to the local source as described above.


## Installer

Your packaged project is simply a file.
However, you might want to distribute an installer to your users.
Installers can be created simply in box by typing:

```
box installer
```

Optionally, you can run the installer with the `-v`/`--verbose` flag.
This will provide you with more information on the process, if available.

This will create an installer based on the platform and type of project for you
in the `target/release` folder.

!!! note
    A packaged binary must already be present in the `target/release` folder.
    If it isn't, you will be prompted to package the project first.

### CLIs

{% include-markdown ".includes/installer_cli.md" %}

### GUIs

In order to package a GUI,
you should have an icon file in an `assets` folder in your project.
For Linux, the icon file should be a `svg`, `png`, `jpg`, or `jpeg` file.
For Windows, the icon file should be a `ico` file.
In either case, the icon file(s) must be named `icon.<ext>`,
where `<ext>` is the file extension.
If multiple icons are available,
order of preference is `svg`, `png`, `jpg`, `jpeg`.

!!! note
    Creating an installer will associate the GUI with the PyApp executable, not with the actual Python process.
    Please read up on what you need to do in order to have the icon show up in the taskbar or dock.
    For `PyQt`, some information can, e.g., be found
    [here](https://www.geeksforgeeks.org/how-to-set-icon-to-a-window-in-pyqt5/).

{% include-markdown ".includes/installer_gui.md" %}

## Cleaning your project

If you want to clean the project, run:

```
box clean
```

By default, this will delete the `dist`, `build`, and `release` folder.
See the [CLI documentation](cli.md) for more information on the `clean` command,
e.g., if you only want to clean a specific subfolder.

## Remove the initialization

If you want to uninitialize the project,
type:

```
box uninit
```

This will remove the `[tool.box]` section from your `pyproject.toml` file.
If you provide the `-c`/`--clean` flag as well, the `dist`, `build`, and `release` folders will be deleted prior to uninitializing.
