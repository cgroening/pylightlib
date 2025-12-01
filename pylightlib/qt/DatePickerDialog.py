"""
pylightlib.qt.DatePickerDialog
==============================

Simple dialog window with a calendar-based date picker.

This module defines the `DatePickerDialog` class, a QDialog with a QDateEdit
widget that allows users to select a date using a popup calendar.

Main features:

- Pre-selects the current date on open
- Provides OK and Cancel buttons
- Can return the selected date as a formatted string
- Accepts a formatted date string to prefill the picker

Useful for compact date input dialogs in PySide6-based applications.

"""


# Libs
from datetime import datetime

# == Qt imports (use external folder when app is bundled for LGPL conformity) ==
from pylightlib.msc.SysPathHandler import SysPathHandler

SysPathHandler().set_new_sys_path()
try:
    from PySide6.QtCore import QDate  # type: ignore # noqa
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QDateEdit  # type: ignore # noqa
    from PySide6.QtWidgets import QDialogButtonBox  # type: ignore # noqa
except ImportError as e:
    print(f'Import Error ({__file__}):\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()


class DatePickerDialog(QDialog):
    """
    Dialog window with a date picker.

    Attributes
    ----------
    date_edit : QDateEdit
        QDateEdit widget for date selection.
    button_box : QDialogButtonBox
        QDialogButtonBox for OK and Cancel buttons.
    """
    date_edit: QDateEdit
    button_box: QDialogButtonBox

    def __init__(self, parent=None):
        """
        Initializes the date picker dialog.

        Parameters
        ----------
        parent : object, optional
            The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Datum auswählen")
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create QDateEdit with calendar popup
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())  # set date to today
        layout.addWidget(self.date_edit)

        # Buttons: OK and Cancel
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_selected_date(self) -> None:
        """
        Returns the selected date as a string.

        Returns
        -------
        str
            The selected date in the format DD.MM.YYYY.
        """
        return self.date_edit.date().toString("dd.MM.yyyy")

    def set_selected_date(self, date_string: str) -> None:
        """
        Sets the selected date based on the given string.

        Parameters
        ----------
        date_string : str
            The date string in the format DD.MM.YYYY.
        """
        date = datetime.strptime(date_string, '%d.%m.%Y')
        self.date_edit.setDate(date)
