"""
pylightlib.tk.PyLightWindow
===========================

Tkinter-based application window with color scheme, DPI support,
and persistent layout saving.

Author:
    Corvin Gröning

Date:
    2025-03-21

Version:
    0.1

This module provides the `PyLightWindow` class, a subclass of `tk.Tk`, designed
to serve as the main window for applications using the PyLight Framework.

It enhances the standard Tkinter window with the following features:
- Platform-specific optimizations (e.g., DPI scaling on Windows)
- Automatic saving and restoring of window size and position via `AppStorage`
- Unified widget styling based on a centralized `DefaultColorScheme`
- Predefined widget constructors for common GUI elements such as buttons,
  entries, listboxes, text boxes, and labels, wrapped in styled
  containers (FramedWidget)
- Scrollbar and theme configurations for consistent look & feel
- Utility method for simple button animation (blinking effect)

This class acts as the foundation for PyLight-based GUIs, encouraging a clean
and consistent visual style across platforms while abstracting away many
low-level Tkinter details.

"""

# Libs
import platform
import tkinter as tk
import tkinter.ttk as ttk

# PyLightFramework
from pylightlib.tk.DefaultColorScheme import DefaultColorScheme
from pylightlib.io.AppStorage import AppStorage
from pylightlib.tk.FramedWidget import FramedWidget
from pylightlib.tk.EditableListbox import EditableListbox
from pylightlib.tk.ScrollTextBox import ScrollTextBox

try:
    from pylightlib.tk.PyLightTk_Windows import PyLightTk_Windows
except ImportError:
    pass


class PyLightWindow(tk.Tk):
    """
    This class inherits tkinter.Tk. A Tkinter window is created which contains
    a main frame for the widgets to be placed in.
    Before the window is closed its size and position will be saved in the
    AppStorage.

    The window has a color scheme which is used to set the colors of the
    widgets.

    Attributes:
        color_scheme: Color Scheme for the window. Can be an instance of
                      DefaultColorScheme or a class that inherited
                      DefaultColorScheme.
        os_name:   Name of the operating system: "Darwin" (Mac), "Windows" or
                   "Linux".
        main_frm:  Main Frame of the window for all widgets to be placed in.
        ttk_style: ttk.Style object for the window.
    """
    color_scheme: DefaultColorScheme
    os_name: str
    main_frm: ttk.Frame
    ttk_style: ttk.Style


    def __init__(self, title: str, geometry: str,
                 color_scheme: DefaultColorScheme, *args, **kwargs):
        """
        Creates an instance of tkinter.Tk and sets the size and title of the
        window.

        Args:
            title:        Title of the window.
            geometry:     Size of the window.
            color_scheme: Color Scheme for the window. Can be an instance of
                          DefaultColorScheme or a class that inherited
                          DefaultColorScheme.
            *args:        Variable length argument list.
            **kwargs:     Arbitrary keyword arguments.
        """
        tk.Tk.__init__(self, *args, **kwargs)

        # Get arguments
        self.geometry_str = geometry
        self.title_str = title
        self.color_scheme = color_scheme

        # Get os name
        self.os_name = platform.system()

        # Create style, Tk window and main frame
        self.style()
        self.os_settings()
        self.window_settings()
        self.create_main_frame()

    def style(self) -> None:
        """
        Creates a ttk style using the given color scheme and configures it.

        For most widgets .TLabel is used instead of .TButton, TEntry, etc.
        otherwise it would not be possible to set a background color.
        """
        # Create ttk style
        s = ttk.Style(self)
        s.theme_use('clam')  # ('aqua', 'clam', 'alt', 'default', 'classic')
        self.ttk_style = s
        scfg, smap = s.configure, s.map
        clr: DefaultColorScheme = self.color_scheme

        # Frame
        scfg('TFrame', foreground=clr.app['fg'], background=clr.app['bg'])

        # Set border color of framed widgets
        FramedWidget.default_border_color = (clr.app['accent4'],  # !active
                                             clr.app['accent5'])  # active color

        # Scrollbar
        # TODO: Only change this when on windows
        # scfg("Vertical.TScrollbar", width=30)
        # scfg("Vertical.TScrollbar", arrowsize=30)
        # scfg("Horizontal.TScrollbar", width=30)
        # scfg("Horizontal.TScrollbar", arrowsize=30)

        for sbar in ['Vertical', 'Horizontal']:
            scfg(f'{sbar}.TScrollbar', relief='solid',
                        troughcolor=clr.app['accent1'],
                        bordercolor=clr.app['accent2'],
                        # background=clr.app['accent3'],
                        arrowcolor=clr.app['accent5'],
                        lightcolor=clr.app['accent4'],
                        darkcolor=clr.app['accent4']
                 )
            smap(f'{sbar}.TScrollbar',
                 background=[('!active', clr.app['accent3']),
                             ('active', clr.app['accent4'])])

        # Label
        scfg('TLabel', foreground=clr.app['fg'], background=clr.app['bg'])

        # Button
        smap('button.TLabel',
             foreground=[('pressed',  clr.btn['fg_pressed']),
                         ('active',   clr.btn['fg_active']),
                         ('!pressed', clr.btn['fg'])],
             background=[('pressed',  clr.btn['bg_pressed']),
                         ('active',   clr.btn['bg_active']),
                         ('!pressed', clr.btn['bg'])],
             relief=[('pressed',  clr.btn['relief_pressed']),
                     ('!pressed', clr.btn['relief_!pressed'])])

        # Light button (same background color as window)
        smap('light_button.TLabel',
             foreground=[('pressed',  clr.btn['fg_pressed']),
                         ('active',   clr.btn['fg_active']),
                         ('!pressed', clr.btn['fg'])],
             background=[('pressed',  clr.btn['bg_pressed']),
                         ('active',   clr.btn['bg_active']),
                         ('!pressed', clr.app['accent1'])],
             relief=[('pressed',  clr.btn['relief_pressed']),
                     ('!pressed', clr.btn['relief_!pressed'])])

        # Button Animation
        smap('button_animation.TLabel',
             foreground=[('!pressed', clr.btn['fg_pressed'])],
             background=[('!pressed', clr.btn['bg_pressed'])])

        # F1F12 bar button
        scfg('button_pressed.TLabel',
             foreground=clr.btn['fg_pressed'],
             background=clr.btn['bg_pressed'])

        # Style of the label of a switch
        scfg('switch_button_label_on.TLabel', background=clr.switch['on'])
        scfg('switch_button_label_off.TLabel', background=clr.switch['off'])

        # Style of the label of a dial
        scfg('dial_button_label.TLabel', background=clr.app['accent3'])

        # Entry (TLabel)
        scfg('entry.TLabel', insertcolor=clr.app['accent5'])
        smap('entry.TLabel',
              foreground=[('!pressed', clr.app['fg'])],
              background=[('!pressed', clr.app['accent1'])],
              relief=[('!pressed', 'flat')])

        # Entry (TEntry)
        scfg('entry.TEntry', insertcolor=clr.app['fg_highlight'])
        smap('entry.TEntry',
              foreground=[('!pressed', clr.app['fg'])],
              background=[('!pressed', clr.app['accent1'])],
              fieldbackground=[('!pressed', clr.app['accent1']),
                               ('!focus', clr.app['accent1'])],
              relief=[('!pressed', 'flat')])
        scfg('entry.TEntry', padding=(4, 4, 4, 4))
        scfg('entry.TEntry', bordercolor=[('focus', clr.app['accent1'])])
        smap('entry.TEntry', lightcolor=[('focus', clr.app['accent1'])])
        smap('entry.TEntry', bordercolor=clr.app['accent1'])

        # Notebook (= Tabbed Control)
        # TODO: set colors in color scheme
        smap('TNotebook',
             background=[('!selected', '#091b44')])
        smap('TNotebook.Tab',
             background=[('selected', '#1540a5'), ('!selected', 'black')],
             foreground=[('selected', 'white'), ('!selected', 'white')])

    def listbox_style(self, lbox: EditableListbox) -> None:
        """
        Sets the foreground and background color of a listbox to values from the
        ColorScheme.

        Args:
            lbox: Listbox that should be styled.
        """
        clr: DefaultColorScheme = self.color_scheme
        lbox.configure(bg=clr.app['accent1'],
                       fg=clr.app['fg'],
                       selectbackground=clr.app['accent2'],
                       selectforeground=clr.app['fg'],
                       activestyle='none')

    def os_settings(self) -> None:
        """
        Sets operating system-specific settings.

        MacOS:
            - Binds the CMD+Q shortcut to the on_close method.

        Windows:
            - Sets scaling for high dpi screens.
            - Makes scrollbars larger (high dpi scaling makes them too small).
        """
        # MacOS
        if self.os_name == 'Darwin':
            # Binding for "Window closes" (triggered by CMD+Q shortcut)
            self.createcommand("tk::mac::Quit", lambda: self.on_close())

        # Windows
        if self.os_name == 'Windows':
            # Set scaling for high dpi screens
            PyLightTk_Windows.high_dpi_scaling(self)

            # Make scrollbars larger (high dpi scaling makes them too small)
            self.ttk_style.configure("Vertical.TScrollbar", arrowsize=27)
            self.ttk_style.configure("Horizontal.TScrollbar", arrowsize=27)

    def window_settings(self) -> None:
        """
        Configures the tk window (size, title, bindings).
        """
        # Window size and title
        self.geometry(self.geometry_str)
        self.title(self.title_str)

        # Expand the content of the window to width and height of it
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Binding for "Window closes" (triggered by X-btn on Win / CMD+Q on Mac)
        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def create_main_frame(self) -> None:
        """
        Creates the main frame which contains all widgets.
        """
        self.main_frm = ttk.Frame(master=self, padding=[10, 10, 10, 10])  # type: ignore
        self.main_frm.grid(row=0, column=0, sticky='nesw')

    def show(self) -> None:
        """
        Displays the window.
        """
        self.focus_set()  # Necessary for the FnKey-bindings
        self.mainloop()

    def on_close(self) -> None:
        """
        Callback that is run when the window gets closed. Saves the size and
        position of the window in the AppStorage and destroys the window.
        """
        # Get current window size and position
        b, h = self.winfo_width(), self.winfo_height()
        x, y = self.winfo_x(), self.winfo_y()

        # Generate geometry string and save in AppStorage
        window_geometry = f'{b}x{h}+{x}+{y}'
        AppStorage().set('main_window_geometry', window_geometry)

        print(self.winfo_width())
        # Destroy window
        self.destroy()

    # noinspection PyArgumentList
    def button_animation(self, btn: tk.Button) -> None:
        """
        Makes a button blink for 1 second.

        Args:
            btn: Button that should.
        """
        for i in range(1, 10):
            if not i % 2:  # i ist ungerade
                btn.after(i * 100, lambda: btn.configure(
                    style='button_animation.TLabel'))  # type: ignore
            else:
                btn.after(i * 100, lambda: btn.configure(style='button.TLabel'))  # type: ignore

    def button(self, master, *args, **kwargs) -> FramedWidget:
        """
        Returns a FramedWidget object for a button.

        Args:
            master:   Parent widget.
            *args:    Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The Button.
        """
        return FramedWidget(master=master, *args, **kwargs, widget='button')  # type: ignore

    def entry(self, master, *args, **kwargs) -> FramedWidget:
        """
        Returns a FramedWidget object for an entry.

        Args:
            master:   Parent widget.
            *args:    Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The Entry.
        """
        return FramedWidget(master=master, *args, **kwargs, \
                            widget='entry', \
                            bordercolor=(self.color_scheme.app['accent4'], \
                                         self.color_scheme.app['accent6']))   # type: ignore

    def textbox(self, master, *args, **kwargs) -> ScrollTextBox:
        """
        Returns an object of ScrollTextBox.

        Args:
            master:   Parent widget.
            *args:    Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The ScrollTextBox.
        """
        textbox = ScrollTextBox(master=master, *args, **kwargs)
        textbox.text_widget.config(
            borderwidth=1, relief='solid', highlightthickness=1,
            highlightbackground=self.color_scheme.app['accent4'],
            highlightcolor=self.color_scheme.app['accent6'],
            font=('pt mono', 15))

        return textbox


    def label(self, master, *args, **kwargs):
        """
        Returns a FramedWidget object for a label.

        Args:
            master:   Parent widget.
            *args:    Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The Label.
        """
        return ttk.Label(master=master, *args, **kwargs)

    def listbox(self, master, *args, **kwargs) -> FramedWidget:
        """
        Returns a FramedWidget object for a listbox.

        Args:
            master:   Parent widget.
            *args:    Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The Listbox.
        """
        return FramedWidget(master=master, *args, **kwargs, \
                            widget='listbox', \
                            bordercolor=(self.color_scheme.app['accent4'], \
                                         self.color_scheme.app['accent6']) \
                            )  # type: ignore
