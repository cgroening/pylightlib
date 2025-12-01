"""
pylightlib.tk.ViewBase
===========================

Abstract base class for all application views using the PyLightWindow framework.

This module provides the `ViewBase` class, a foundational component for building
graphical user interface views within the PyLightFramework. It implements basic
window behavior such as instantiating the main window, managing geometry,
handling the close event, and offering hooks for widget creation.

`ViewBase` uses the Singleton design pattern to ensure only one instance of each
view exists during runtime. It relies on the `PyLightWindow` class as a base for
the Tkinter root window and provides utility methods to control positioning and
styling.

Intended to be subclassed by concrete view implementations.

Main features:

- Ensures single instance through Singleton metaclass
- Standardized window setup using `PyLightWindow`
- Optional centering of window geometry
- Basic close event handling
- Override-ready `create_widgets()` method for custom UI

"""

# PyLightFramework
from pylightlib.msc.Singleton import Singleton
from pylightlib.tk.PyLightWindow import PyLightWindow


class ViewBase (metaclass=Singleton):
    """
    Base class for all views.

    Attributes
    ----------
    kwargs : dict or None
        Kwargs given at initialization.
    root : PyLightWindow
        Instance of the tk root.
    geometry : str
        Position and size of the tk window.
    clr : object or None
        Reference to the color scheme.
    title : str or None
        Title of the tk window.
    """
    kwargs = None
    root: PyLightWindow
    geometry: str = '500x300+500+300'
    clr = None
    title: str | None = None


    def __init__(self, **kwargs):
        """
        Creates a tk window and adds labels for title, version and info text.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments passed to the window initialization.
        """
        self.kwargs = kwargs
        self.create_window()
        self.create_widgets()
        self.check_geometry()

    def create_window(self):
        """
        Create tk root and widgets.

        Instantiates a PyLightWindow, sets up the close protocol,
        and brings the window to the front.
        """
        # noinspection PyTypeChecker

        # Create instance of PyLightWindow
        self.root = PyLightWindow(**self.kwargs,
                                  title=self.title,
                                  geometry=self.geometry,
                                  color_scheme=self.clr)
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Bring window to front
        self.root.lift()
        self.root.after(1, lambda: self.root.focus_force())

    def check_geometry(self) -> None:
        """
        Place the window in the center of the screen if the geometry is None.
        """
        if self.geometry is None:
            self.center_window()


    def center_window(self) -> None:
        """
        Place the window in the center of the screen.

        Calculates the screen dimensions, window size, and titlebar height
        to position the window centrally with a vertical offset for the dock/taskbar.
        """
        # Get screen width and height
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # Get window width and height (without titlebar)
        self.root.update_idletasks()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()

        # Get titlebar height
        titlebar_h = self.root.winfo_rooty() - self.root.winfo_y()

        # Calculate coordinates to place window in center of screen and
        # consider and offset in height of -85 px for Mac dock/Win task bar
        win_x = (screen_w - win_w) / 2
        win_y = (screen_h - win_h - titlebar_h) / 2 - 85

        # Set window geometry
        self.root.geometry('%dx%d+%d+%d' % (win_w, win_h, win_x, win_y))

    def on_closing(self) -> None:
        """
        Callback that is triggered when the window is closed.

        Destroys the root window when the user closes the application.
        """
        self.root.destroy()

    def create_widgets(self) -> None:
        """
        Creates the widgets for the tk window. To be overwritten.

        This method should be overridden by subclasses to implement
        custom widget creation for their specific views.
        """
        pass
