"""
pylightlib.tk.AboutView
=======================

View class for displaying application information in a simple about window.

Author:
    Corvin Gröning

Date:
    2025-09-01

Version:
    0.1

This module defines the `AboutView` class, a Tkinter-based window that
displays information about the application, including its name, version,
and additional descriptive text.

Features:

- Inherits from `ViewBase`
- Uses a shared `ColorScheme` for styling
- Displays the app name, version, and info text using consistent fonts
- Easily extendable with more UI elements via `create_widgets()`

"""

# PyLightFramework
from pylightlib.tk.ViewBase import ViewBase
from pylightlib.tk import DefaultColorScheme
from pylightlib.tk.PyLightWindow import PyLightWindow


class AboutView(ViewBase):
    """
    About Window which displays the title, version and info text.

    Attributes:
        clr:       Reference to the color scheme.
        geometry:  Position and size of the tk window.
        title:     Window title.
        app_name:  Name of the application.
        version:   Version of the application.
        info_text: Info text of the application.
    """
    clr: DefaultColorScheme  # type: ignore
    geometry: str
    title: str
    app_name: str
    version: str
    info_text: str


    def __init__(self, color_scheme: DefaultColorScheme, geometry: str, win_title: str,  # type: ignore
                 app_name: str, version: str, info_text: str, **kwargs):
        """
        Initializes the AboutView with window settings and app details.

        Args:
            color_scheme: The color scheme to use.
            geometry:     Window size and position.
            win_title:    Title of the window.
            app_name:     Name of the application.
            version:      Application version.
            info_text:    Additional info text.
            **kwargs:     Extra arguments passed to the base class.
        """
        # Create tk window
        self.clr = color_scheme
        self.geometry = geometry
        self.title = win_title
        self.app_name = app_name
        self.version = version
        self.info_text = info_text
        super().__init__(**kwargs)

    def create_widgets(self):
        """
        Creates labels for title, version and info text.
        """
        root: PyLightWindow = self.root
        mfrm = self.root.main_frm

        root.label(master=mfrm, font=('Arial', 20), text=self.app_name).pack()
        root.label(master=mfrm, font=('Arial', 20), text=self.version).pack()
        root.label(master=mfrm, font=('Arial', 14), text=self.info_text).pack()
