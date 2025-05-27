"""
pylightlib.qt.CustomDateEdit
============================

QDateEdit widget with support for empty values and flexible date handling.

Author:
    Corvin Gröning

Date:
    2025-03-21

Version:
    0.1

This module defines the `CustomDateEdit` widget, an extended version of Qt's
`QDateEdit` that allows displaying and handling an empty (unset) date field.
The class provides user-friendly logic for date input and display, including:

- Displaying a placeholder text when no date is set
- Converting between UNIX timestamps and date strings
- Automatically setting today's date when the calendar is opened on an empty
  field
- Compatibility with the PyLightFramework using custom `DateTime` conversions

Useful for form inputs where the date is optional or can be cleared.

"""

# Libs
from datetime import datetime

# PyLightFramework
from pylightlib.msc.DateTime import DateTime

# == Qt imports (use external folder when app is bundled for LGPL conformity) ==
from pylightlib.msc.SysPathHandler import SysPathHandler

SysPathHandler().set_new_sys_path()
try:
    from PySide6.QtCore import QDate, QDateTime, Qt  # type: ignore # noqa
    from PySide6.QtWidgets import QDateEdit          # type: ignore # noqa
except ImportError as e:
    print(f'Import Error ({__file__}):\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()


class CustomDateEdit(QDateEdit):
    """
    QDateEdit Widget that can be empty.
    """
    def __init__(self, /):
        super().__init__()

        # Widget settings
        self.setCalendarPopup(True)
        self.setDisplayFormat("dd.MM.yyyy")
        self.clear_date()

        # Connect events
        self.dateChanged.connect(self.on_date_changed)
        self.lineEdit().textChanged.connect(self.on_date_changed)

    def clear_date(self) -> None:
        """
        Workaround which allows the widget to display an empty box is not date
        is set.
        """
        self.setSpecialValueText(' ')        # Must be ' ', not empty
        self.setMinimumDate(QDate(1, 1, 1))  # Set empty date
        self.setDate(QDate(1, 1, 1))         # Empty start value
        self.lineEdit().setPlaceholderText("Kein Datum")

    def set_date_timestamp(self, timestamp) -> None:
        """
        Set the date of the widget.

        Args:
            timestamp: UNIX timestamp of the date.
        """
        if timestamp is not None and timestamp != '':
            # Convert given time stamp to date and set date of widget
            date_str = str(DateTime.timestamp_to_date(int(timestamp)))
            date_formatted = datetime.strptime(date_str, '%d.%m.%Y')
            self.setDate(date_formatted)
        else:
            # Display an empty widget
            self.clear_date()

    def get_date_str(self):
        """
        Returns the date as a string in the format DD.MM.YYYY.

        Returns:
            Date string in the format DD.MM.YYYY or None of no date is set.
        """
        if self.lineEdit().text() == '' or self.lineEdit().text() == ' ':
            return None
        else:
            return self.date().toString('dd.MM.yyyy')

    def get_date_timestamp(self):
        """
        Returns the date as a timestamp.

        Returns:
            UNIX timestamp or None of no date is set.
        """
        if self.lineEdit().text() == '' or self.lineEdit().text() == ' ':
            return None
        else:
            return DateTime.date_to_timestamp(self.get_date_str())

    def on_date_changed(self) -> None:
        """
        Is triggered if the date of the widget changes. Sets the date to nothing
        if the value of the text box is empty/removed by the user.
        """
        if self.lineEdit().text() == '' or self.lineEdit().text() == ' ':
            self.clear_date()

    def mousePressEvent(self, event) -> None:
        """
        Is triggered if the user clicks on the dropdown. Set the date to today
        if it's empty. Otherwise, the start date would be 14.09.1752 because of
        the settings made in self.clear_data().

        Args:
            event
        """
        # Call event that is overridden by this one
        super().mousePressEvent(event)

        # Set date to today
        if self.lineEdit().text() == ' ' or self.lineEdit().text() is None:
            self.setDate(QDate.currentDate())
