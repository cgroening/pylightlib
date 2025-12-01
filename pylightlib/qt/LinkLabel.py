"""
pylightlib.qt.LinkLabel
=======================

Clickable QLabel that opens a URL when clicked.

This module defines the `LinkLabel` class, a QLabel extension that behaves
like a hyperlink. When clicked, it opens a predefined URL in the user's
default browser.

Features:

- Underlined text with a pointer cursor to indicate clickability
- URL can be set via `set_url(url: str)`
- Opens the link on mouse click using `QDesktopServices`

Useful for displaying external links in PySide6 applications.

"""

from typing import Any

# == Qt imports (use external folder when app is bundled for LGPL conformity) ==
from pylightlib.msc.SysPathHandler import SysPathHandler

SysPathHandler().set_new_sys_path()
try:
    from PySide6.QtCore import QUrl                          # type: ignore # noqa
    from PySide6.QtGui import QDesktopServices, QMouseEvent  # type: ignore # noqa
    from PySide6.QtWidgets import QLabel                     # type: ignore # noqa
except ImportError as e:
    print(f'Import Error ({__file__}):\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()


class LinkLabel(QLabel):
    """
    Label that inherits QLabel.

    An URL can be set which will be opened if the user clicks on the label.

    Attributes
    ----------
    _url : str or None
        Internet address.
    """
    _url: str | None = None


    def __init__(self, text: str, parent: Any = None):
        """
        Calls the super class and makes the label underlined.

        Parameters
        ----------
        text : str
            Caption of the label.
        parent : Any, optional
            Parent widget.
        """
        super().__init__(text, parent)
        self.setStyleSheet('text-decoration: underline; cursor: pointer;')

    def set_url(self, url: str) -> None:
        """
        Sets the URL which will be opened if the user clicks on the label.

        Parameters
        ----------
        url : str
            Internet address.
        """
        self._url = url

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Event that is triggered when the user clicks on the label.

        Opens the URL.

        Parameters
        ----------
        event : QMouseEvent
            The mouse event object.
        """
        QDesktopServices.openUrl(QUrl(self._url))
