"""
pylightlib.tk.ScrollTextbox
===========================

A scrollable text box widget using Tkinter and ttk.

Author:
    Corvin Gröning

Date:
    2025-03-21

Version:
    0.1

This module defines the `ScrollTextBox` class, a reusable Tkinter widget that
combines a `Text` widget with a vertical scrollbar inside a `ttk.Frame`. It
simplifies the creation of scrollable text areas in GUI applications.

The text widget supports word wrapping and is configured to expand and fill the
available space. The vertical scrollbar is automatically synchronized with the
text box's scrolling behavior.

Typical use cases include log viewers, code editors, comment sections, or any UI
that requires multi-line text input or display with vertical scrolling.
"""

import tkinter as tk
import tkinter.ttk as ttk


class ScrollTextBox(ttk.Frame):
    """
    Vertically scrollable text box.

    This class inherits ttk.Frame. It contains a text box and a vertical
    scrollbar.

    Attributes:
        text_widget (tk.Text): Text box object.
        scrollbar (ttk.Scrollbar): Scroll bar object.
    """

    text_widget: tk.Text
    scrollbar: ttk.Scrollbar


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Implement stretchability
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a text widget
        self.text_widget = tk.Text(self, wrap='word')
        self.text_widget.grid(row=0, column=0, sticky='nsew', padx=(0, 2))

        # Create a scrollbar and associate it with text widget
        self.scrollbar = ttk.Scrollbar(self, command=self.text_widget.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.text_widget['yscrollcommand'] = self.scrollbar.set
