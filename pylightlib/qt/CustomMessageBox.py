"""
pylightlib.qt.CustomMessageBox
==============================

Custom wrapper around QMessageBox for simple info and confirmation dialogs.

Author:
    Corvin Gröning

Date:
    2025-03-21

Version:
    0.1

This module defines the `CustomMessageBox` class, a small extension of Qt's
`QMessageBox` that simplifies showing message dialogs in PySide6.

It provides two main methods:

- `info(text: str)`: Shows an information dialog with a Close button.
- `yes_no(text: str)`: Shows a Yes/No dialog and returns the user’s choice.

Useful for displaying quick info or asking for confirmation in a clean,
consistent way. Intended to be initialized with a parent widget.

"""

# == Qt imports (use external folder when app is bundled for LGPL conformity) ==
from pylightlib.msc.SysPathHandler import SysPathHandler

SysPathHandler().set_new_sys_path()
try:
    from PySide6.QtWidgets import QMessageBox  # type: ignore # noqa
except ImportError as e:
    print(f'Import Error ({__file__}):\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()


class CustomMessageBox(QMessageBox):
    """
    Displays a message box with an OK button or Yes/No buttons.

    Attributes:
        parent: Parent of the info box.
    """
    parent = None

    def __init__(self, parent):
        """
        Calls the super class.

        Args:
            parent: Parent of the info box.
        """
        super().__init__()
        self.parent = parent


    def info(self, text: str) -> None:
        """
        Displays an info message.

        Args:
            text:   Text of the info box
        """
        self.setIcon(QMessageBox.Icon.Information)
        self.setWindowTitle('Info')
        self.setStandardButtons(QMessageBox.StandardButton.Close)
        self.setText(text)
        self.exec()

    def yes_no(self, text: str) -> bool:
        """
        Displays a confirmation box with yes/no buttons.

        Args:
            text:   Text of the info box

        Returns:
            True if the user clicked "yes", False if the user clicked no.
        """
        self.setIcon(QMessageBox.Icon.Question)
        self.setWindowTitle('Bestätigung')
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        self.setText(text)
        result = self.exec()

        if result == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False
