# Clean the project folder

from pathlib import Path
import shutil

import box.formatters as fmt


class CleanProject:
    """Cleaning class for the project folder."""

    def __init__(
        self,
        dist: bool = False,
        build: bool = False,
        target: bool = False,
        source_pyapp: bool = False,
        pyapp_folder: bool = False,
    ) -> None:
        """Initialize the CleanProject class.

        Attention: These are "clean only" options. If all options are false,
        the whole project (all folders) will be cleaned.

        :param dist: Clean the `dist` folder?
        :param build: Clean the `build` folder?
        :param target: Clean the `target` folder?
        :param source_pyapp: Clean the `pyapp-source.tar.gz` file?
            Ignores `target` value.
        :param pyapp_folder: Clean the `pyapp` folder(s) in `build`?
            Ignores `target` value.
        """
        self.source_pyapp = source_pyapp
        self.pyapp_folder = pyapp_folder

        options = [dist, build, target, source_pyapp, pyapp_folder]

        if source_pyapp or pyapp_folder:
            if build:
                fmt.info("Build folder flag `-b`, `--build` ignored.")
            build = False

        self._echo_string = ""
        self._cleaned_whole_project = False

        # if all options are None, clean all folders
        if not any(options):
            self.folders_to_clean = ["dist", "build", "target"]
            self._cleaned_whole_project = True
        else:
            self.folders_to_clean = []
            if dist:
                self.folders_to_clean.append("dist")
            if build:
                self.folders_to_clean.append("build")
            if target:
                self.folders_to_clean.append("target")

    def clean(self):
        """Clean the project according to the options selected."""
        # delete all folders_to_clean and files therein
        self._clean_folders()
        self._clean_build_folder()

        # echo stuff
        if self._cleaned_whole_project and self._echo_string != "":
            fmt.success("The whole project was cleaned.")
        else:
            if self._echo_string != "":
                fmt.success(self._echo_string)
            else:
                fmt.info("Nothing to clean.")

    def _clean_folders(self):
        """Clean the main folders."""
        folder_cleaned = []
        for folder in self.folders_to_clean:
            folder_path = Path.cwd().joinpath(folder)
            if folder_path.exists():
                shutil.rmtree(folder_path)
                folder_cleaned.append(folder)

        if folder_cleaned:
            self._echo_string += f"Folder(s) {', '.join(folder_cleaned)} cleaned.\n"

    def _clean_build_folder(self):
        """Clean the pyapp specific file/folder(s) in the build folder."""
        out_string = ""
        if self.source_pyapp:
            pyapp_source = Path.cwd().joinpath("build/pyapp-source.tar.gz")
            if pyapp_source.exists():
                pyapp_source.unlink()
                out_string += "pyapp-source.tar.gz"
        if self.pyapp_folder:
            pyapp_folders = []
            if Path.cwd().joinpath("build").exists():
                for file in Path.cwd().joinpath("build").iterdir():
                    if file.is_dir() and file.name.startswith("pyapp-"):
                        pyapp_folders.append(file)
                for folder in pyapp_folders:
                    shutil.rmtree(folder)
                if pyapp_folders:
                    if out_string != "":
                        out_string += ", "
                    out_string += "pyapp folder(s)"

        if out_string != "":
            self._echo_string += f"{out_string} cleaned.\n"
