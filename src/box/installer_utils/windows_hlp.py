"""Helper routines for creating installers on Windows."""

from pathlib import Path


def nsis_cli_script(project_name: str, installer_name: str, binary_path: Path):
    """Create NSIS script for CLI installer.

    :param project_name: Name of the project
    :param installer_name: Name of the installer to be produced by NSIS
    :param binary_path: Path to the binary to be installed
    """
    return rf"""; NSIS script to create installer for {project_name}

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "{project_name}"
  OutFile "{installer_name}"
  Unicode True

  ;Default installation folder
  InstallDir "$LOCALAPPDATA\{project_name}"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\{project_name}" ""

  ;Request application privileges
  RequestExecutionLevel user


;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY

  !insertmacro MUI_PAGE_INSTFILES

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "{project_name}" SecInst

  SetOutPath "$INSTDIR"

  ; Files for {project_name}
  File "{binary_path.name}"

  ;Store installation folder
  WriteRegStr HKCU "Software\{project_name}" "" $INSTDIR
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\{project_name}" "DisplayName" "{project_name}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\{project_name}" "UninstallString" '"$INSTDIR\Uninstall-{project_name}.exe"'

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall-{project_name}.exe"\

  ; Add the binary path to the PATH environment variable
  nsExec::Exec 'echo %PATH% | find "$INSTDIR"'
  Pop $0   ; gets result code

  ${{If}} $0 = 0
    nsExec::Exec 'setx PATH=%PATH%;$INSTDIR'
  ${{EndIf}}

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecInst ${{LANG_ENGLISH}} "Selection."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecInst}} $(DESC_SecInst)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"


  ; Delete {project_name} folder
  Delete "$INSTDIR\{binary_path.name}"
  Delete "$INSTDIR\Uninstall-{project_name}.exe"

  RMDir "$INSTDIR"

  ; Delete PyApp virtual environment
  RMDir /r "$LOCALAPPDATA\pyapp\data\{project_name}"

  ; Delete registry key
  DeleteRegKey /ifempty HKCU "Software\{project_name}"
  DeleteRegKey /ifempty HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\{project_name}"

SectionEnd
"""


def nsis_gui_script(
    project_name: str, installer_name: str, binary_path: Path, icon_path: Path
):
    """Create NSIS script for GUI installer.

    :param project_name: Name of the project
    :param installer_name: Name of the installer to be produced by NSIS
    :param binary_path: Path to the binary to be installed
    :param icon_path: Path to the icon file to be used in the installer
    """
    return rf"""; NSIS script to create installer for {project_name}

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "{project_name}"
  OutFile "{installer_name}"
  Unicode True

  ;Default installation folder
  InstallDir "$LOCALAPPDATA\{project_name}"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\{project_name}" ""

  ;Request application privileges
  RequestExecutionLevel user

;--------------------------------
;Variables

  Var StartMenuFolder

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY

  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\{project_name}"
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"

  !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

  !insertmacro MUI_PAGE_INSTFILES

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "{project_name}" SecInst

  SetOutPath "$INSTDIR"

  ; Files for {project_name}
  File "{binary_path.name}"

  ;Store installation folder
  WriteRegStr HKCU "Software\{project_name}" "" $INSTDIR

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall-{project_name}.exe"

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application

    ;Create shortcuts - if icon file is empty, leave that part away
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\{project_name}.lnk" "$INSTDIR\{binary_path.name}" "" "{str(icon_path.absolute())}"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall-{project_name}.lnk" "$INSTDIR\Uninstall-{project_name}.exe"

  !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecInst ${{LANG_ENGLISH}} "Selection."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecInst}} $(DESC_SecInst)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"


  ; Delete {project_name} folder
  Delete "$INSTDIR\{binary_path.name}"
  Delete "$INSTDIR\Uninstall-{project_name}.exe"

  RMDir "$INSTDIR"

  ; Delete PyApp virtual environment
  RMDir /r "$LOCALAPPDATA\pyapp\data\{project_name}"

  ; Delete start menu entry
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder

  Delete "$SMPROGRAMS\$StartMenuFolder\{project_name}.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall-{project_name}.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"

  ; Delete registry key
  DeleteRegKey /ifempty HKCU "Software\{project_name}"

SectionEnd
"""
