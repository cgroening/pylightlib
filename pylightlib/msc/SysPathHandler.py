"""
pylightlib.msc.SysPathHandler
=============================

Provides functionality to dynamically manipulate `sys.path` and module imports
for loading Qt libraries (e.g., PySide6, shiboken6) from external sources.

Author:
    Corvin Gröning

Date:
    2025-03-21

Version:
    0.1

This module is designed to support LGPL compliance for applications using Qt
bindings by allowing dynamic linking of PySide6 and shiboken6. It ensures that
users can replace these libraries in frozen applications (e.g., .app bundles
on macOS).

Key Features:
- `activate_dynamic_qt_linking`: Configures `sys.path` and import logic for
frozen macOS apps or when debug mode is active.
- `SysPathHandler`: A singleton utility class that handles:
    - Temporarily replacing `sys.path` to load libraries from external
      locations.
    - Cleaning `sys.modules` to avoid importing from the virtual environment
      in debug mode.
    - Restoring the original `sys.path` after external packages are imported.

Platform Support:
- **macOS only** for frozen applications.
- Debug mode also works during development across platforms.

Usage Example (for debug mode or frozen deployment)::

```
SysPathHandler().set_new_sys_path()
try:
    from PySide6 import QtWidgets
except ImportError as e:
    print(f'Import Error ({__file__}):\\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()
```

This approach helps in staying compliant with LGPL by enabling runtime
substitution of Qt libraries by the end-user.

"""

# Libs
import os
import platform
import sys

# PyLightFramework
from pylightlib.msc.Singleton import Singleton


def activate_dynamic_qt_linking(external_libs_folder: str,
                                external_libs_folder_debug_mode: str,
                                debug_mode: bool = False) -> None:
    """
    Enables dynamic linking for Qt packages (PySide6 and shiboken6) to ensure
    LGPL compliance. The folder external_libs_folder must have the same parent
    folder as the .app bundle. This way the user can exchange the PySide/Qt
    file for his own (requirement from the LGPL).

    FROZEN APP ONLY: This functionality only works for bundled/frozen apps.
    During development the Qt packages are imported from the virtual
    environment unless debug mode is enabled. Then, the packages will be
    imported from external_libs_folder_debug_mode.

    MAC ONLY: This is only necessary on macOS, because on Windows cx_freeze
    automatically creates a folder with the .exe and the Qt libs which can be
    exchanged.

    Args:
        external_libs_folder: Name of the folder that contains PySide6 and
                              shiboken6. It must be placed next to the
                              .app bundle.
        external_libs_folder_debug_mode: Absolute path of the external lib
                                         folder - used in debug mode.
        debug_mode: If this is on the Qt files are imported from the absolute
                    path external_libs_folder_debug_mode.
    """
    # Check if the app is frozen (bundled into an .app) and the OS is macOS
    # or if debug mode is activated
    if (getattr(sys, 'frozen', False) and platform.system() == "Darwin")\
            or debug_mode:
        if debug_mode:
            lib_path = external_libs_folder_debug_mode
        else:
            # Get path of app bundle
            app_path = os.path.abspath(
                os.path.join(os.path.dirname(sys.executable), "../../..")
            )

            # Define the folder containing the app bundle as the parent folder
            # for the external libs folder
            lib_path = f'{app_path}/{external_libs_folder}'

        # Adjust sys.path
        SysPathHandler(
            external_libs_path=[lib_path],
            sys_modules=['PySide6', 'shiboken6'],
            debug_mode=debug_mode
        )


class SysPathHandler(metaclass=Singleton):
    """
    This class provides functionality to dynamically manage the `sys.path`
    for loading external libraries/packages. It ensures that specific
    external libraries (e.g., PySide6) are loaded from a designated path,
    allowing compliance with LGPL requirements.

    To allow the debug mode to function correctly the import of external
    packages must be as follows:

        from pylightlib.msc.SysPathHandler import SysPathHandler

        SysPathHandler().set_new_sys_path()
        try:
            from PySide6 import QtWidgets  # Example
        except ImportError as e:
            print(f'Import Error ({__file__}):\n    ' + str(e.msg))
            exit()
        SysPathHandler().restore_sys_path()

    Attributes:
        external_libs_path: A list of absolute paths of folders containing
                            external packages.
        sys_modules:        List of modules to be excluded from `sys.modules`
                            (each module that begins with one of the given
                            strings will be removed).
        original_sys_path:  Backup of the original `sys.path`.
        debug_mode:         If this is on, an app bundle that does NOT contain
                            the packages from external_libs_path will be
                            simulated by temporarily setting sys.path to only
                            the folder given by external_libs_path. Those
                            packages must be imported between the
                            self.set_new_sys_path and self. restore_sys_path
                            call.
    """
    external_libs_path: list[str] | None
    sys_modules: list[str] | None
    original_sys_path: list[str]
    debug_mode: bool


    def __init__(self, external_libs_path: list[str] | None = None,
                 sys_modules: list[str] | None = None,
                 debug_mode: bool = False):
        """
        Initializes the SysPathHandler.

        Args:
            external_libs_path: A list of absolute paths of folders containing
                                external packages.
            sys_modules: List of modules to be excluded from `sys.modules`
                         (each module that begins with one of the given
                         strings will be removed).
            debug_mode:  Indicates if the debug mode is enabled. See the class
                         description for further information.
        """
        self.external_libs_path = external_libs_path
        self.sys_modules = sys_modules
        self.debug_mode = debug_mode

        if external_libs_path is None:
            return

        self.remove_sys_modules()

    def remove_sys_modules(self):
        """
        If debug mode: removes the external packages from sys.module to ensure
        that they are imported from the external folder instead of the venv.
        """
        if not getattr(sys, 'frozen', False) and self.debug_mode:
            # Look for keys in sys.modules that begin with the strings in
            # self.sys_modules and add the full keys to a list
            keys_to_delete: list[str] = []
            for module_name in self.sys_modules:
                for key in sys.modules:
                    if key.startswith(module_name):
                        keys_to_delete.append(key)

            # Delete all found keys from sys.modules
            for key in keys_to_delete:
                del sys.modules[key]

    def set_new_sys_path(self):
        """
        Add the external_libs_paths to `sys.path`. If debug mode is on `sys.path`
        is cleared before that.
        """
        if self.external_libs_path is None:
            return

        # Backup of the original sys.path
        self.original_sys_path = sys.path.copy()

        # If app is not bundled but debug mode is on clear sys.path
        if not getattr(sys, 'frozen', False) and self.debug_mode:
            sys.path = []

        # Add external lib paths to sys.path
        for path in self.external_libs_path:
            sys.path.append(path)

    def restore_sys_path(self):
        """
        Restores the original sys.path before self.set_new_sys_path was called.
        """
        if self.external_libs_path is None:
            return

        sys.path = self.original_sys_path.copy()
