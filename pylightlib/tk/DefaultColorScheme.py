"""
pylightlib.tk.DefaultColorScheme
================================

Provides a default color scheme for consistent theming in tkinter-based UIs.

This module defines the `DefaultColorScheme` dataclass, which contains
dictionaries grouping foreground and background colors used throughout a tkinter
user interface. It centralizes color definitions for the main application frame,
buttons, and toggle switches to promote visual consistency and ease of
customization. The scheme uses a dark theme with cyan and green accents,
designed for modern, accessible UIs.

"""

from dataclasses import dataclass


@dataclass
class DefaultColorScheme:
    """
    This is the default color scheme for the UI.

    _bg are background colors, _fg are foreground colors.

    Attributes
    ----------
    app : dict
        Main application frame color definitions including foreground,
        background and various accent colors.
    btn : dict
        Button color definitions for different states (normal, active, pressed)
        including foreground, background, and relief styles.
    switch : dict
        Toggle switch color definitions for ON and OFF states.
    """

    # Main Frame
    app = {
        'fg': '#EFF3F8',            # white
        'fg_highlight': '#00FCFE',  # cyan
        'bg': '#2A2D30',            # dark gray
        'accent1': '#1C1E20',       # near black
        'accent2': '#313438',       # dark gray
        'accent3': '#3F4447',       # dark/medium gray
        'accent4': '#404448',       # medium gray
        'accent5': '#00252E',       # blue-green
        'accent6': '#005A71',       # lighter blue-green
    }

    # Buttons
    btn = {
        'fg':         app['fg'],
        'fg_active':  app['fg'],
        'fg_pressed': app['fg_highlight'],
        'bg':         app['accent2'],
        'bg_active':  app['accent4'],
        'bg_pressed': app['accent5'],
        'relief_pressed':  'flat',
        'relief_!pressed': 'flat'
    }

    # Switch
    switch = {
        'on': '#359431',   # green
        'off': '#5D6368',  # gray
    }
