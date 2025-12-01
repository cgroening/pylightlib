"""
pylightlib.qt.StatusMessage
===========================

Helper to display timestamped messages in a QStatusBar.

This module defines the `StatusMessage` class, a singleton used to show
messages in a `QStatusBar` with the current date and time prepended.

Features:

- Uses a singleton pattern to ensure only one instance is active
- Displays messages in the format: "[DD.MM.YYYY HH:MMh] Message"
- Requires a `QStatusBar` instance to be passed once via constructor

Useful for logging user actions or system feedback in GUI applications.

"""

# Libs
from datetime import datetime

# PyLightFramework
from pylightlib.msc.Singleton import Singleton

# == Qt imports (use external folder when app is bundled for LGPL conformity) ==
from pylightlib.msc.SysPathHandler import SysPathHandler

SysPathHandler().set_new_sys_path()
try:
    from PySide6.QtWidgets import QStatusBar  # type: ignore # noqa
except ImportError as e:
    print(f'Import Error ({__file__}):\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()


class StatusMessage(metaclass=Singleton):
    """
    This class gets the object of a QStatusBar and then is able to prompt messages with current date and time.

    Attributes
    ----------
    statusbar : QStatusBar
        StatusBar which was created in the View.
    """
    statusbar: QStatusBar


    def __init__(self, statusbar: QStatusBar = None):
        """
        Sets the status bar object.

        Parameters
        ----------
        statusbar : QStatusBar, optional
            Instance of QStatusBar. Leave empty if already set.
        """
        self.statusbar = statusbar

    def show_message(self, message: str) -> None:
        """
        Shows a message in the status bar with current date and time.

        Parameters
        ----------
        message : str
            Message to be displayed.
        """
        # self.statusbar.showMessage(self.date_time_string() + message)
        pass

    def date_time_string(self) -> str:
        """
        Returns a string with the current date and time in the format: "[DD.MM.YYYY - hh:mm h] "

        Returns
        -------
        str
            String with current date and time.
        """
        now = datetime.now()
        formatted_datetime = now.strftime("[%d.%m.%Y %H:%Mh] ")

        return formatted_datetime

