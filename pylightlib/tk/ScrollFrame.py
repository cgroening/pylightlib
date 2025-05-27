"""
pylightlib.tk.ScrollFrame
=========================

A reusable scrollable frame for embedding widgets in Tkinter GUIs.

Author:
    Corvin Gröning

Date:
    2025-03-22

Version:
    0.1

This module defines the `ScrollFrame` class, a utility widget that creates
a scrollable area using a `tk.Canvas` and an embedded `tk.Frame`. It allows
developers to add arbitrary widgets into the inner frame while retaining the
ability to scroll vertically, horizontally, or both.

The class supports:
- Optional vertical/horizontal scrollbars via the `scrollbar` parameter
- Dynamic scroll region resizing when inner content changes
- Mouse wheel event handling (platform-independent) that only activates when
  the mouse is over the scrollable region
- Clean API: attribute access and geometry management are transparently
  delegated to the correct internal frame

This component is ideal for situations where content may exceed the available
space (e.g., forms, dynamic lists, nested UIs) and is fully styled according to
a provided `DefaultColorScheme` instance from the PyLight framework.

"""

import tkinter as tk
from tkinter import ttk

from pylightlib.tk.DefaultColorScheme import DefaultColorScheme


class ScrollFrame:
    """
    A scrollable frame component for Tkinter GUIs.

    The ScrollFrame class creates a composite widget consisting of an outer
    frame containing a canvas and an inner frame. The inner frame can host
    arbitrary widgets while remaining scrollable both vertically and horizontally.

    This class supports optional vertical and/or horizontal scrollbars. It also
    automatically binds mouse wheel events to allow intuitive scrolling when the
    mouse cursor is over the component. This enables multiple scrollable areas
    to coexist in the same application without interfering with each other.

    Attributes:
        color_scheme: The color scheme used to style the frame.
        width:  The width of the scrollable area.
        height: The height of the scrollable area.
        vscrl:  Whether the vertical scrollbar is enabled.
        hscrl:  Whether the horizontal scrollbar is enabled.
        outer_frame: The main container frame holding the canvas and scrollbars.
        inner_frame: The frame inside the canvas where widgets are added.
        vsb:    The vertical scrollbar widget.
        hsb:    The horizontal scrollbar widget.
        canvas: The canvas used to enable scrolling.

    Usage:
        scroll_frame = ScrollFrame(
            root, color_scheme, width=400, height=300, scrollbar='b'
        )
        scroll_frame.pack(fill='both', expand=True)

    Parameters:
        master:       The parent widget.
        color_scheme: The color scheme instance for styling.
        **kwargs:     Optional arguments such as 'width', 'height'
                      and 'scrollbar'.
                      The 'scrollbar' option can be 'v' (vertical),
                      'h' (horizontal), or 'b' (both, default).
    """
    color_scheme: DefaultColorScheme
    width: int
    height: int
    vscrl: bool = True
    hscrl: bool = True
    outer_frame: tk.Frame
    inner_frame: tk.Frame
    vsb: ttk.Scrollbar
    hsb: ttk.Scrollbar
    canvas: tk.Canvas
    attr_outside: set


    def __init__(self, master: tk.Frame, color_scheme: DefaultColorScheme,
                 **kwargs):
        """
        Creates the frame. Optional arguments:

        - width, height: geometry of the frame
        - scrollbar: 'v' (vertical), 'h' (horizontal) oder 'b' (both, default)

        Args:
            master:       The parent widget.
            color_scheme: The color scheme instance for styling.
            **kwargs:     Optional arguments such as 'width', 'height'
                          and 'scrollbar'.
        """
        self.color_scheme = color_scheme

        # Get optional arguments
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        scrollbar = kwargs.pop('scrollbar', 'b')

        # Which scrollbars?
        if scrollbar.startswith('v'):
            self.vscrl = True
            self.hscrl = False
        elif scrollbar.startswith('h'):
            self.vscrl = False
            self.hscrl = True
        else:
            self.vscrl = True
            self.hscrl = True

        # Create frames and canvas
        self.create_outer_frame(master)
        self.create_canvas()
        self.create_inner_frame()

    def __str__(self) -> str:
        """
        Returns the string representation of the outer frame.
        """
        return str(self.outer_frame)

    def __getattr__(self, item) -> object:
        """
        Returns the attribute of the outer frame or inner frame.
        """
        if item in self.attr_outside:
            # Geometry attributes (pack, destroy, tkraise, usw.) will be handed
            # over to self.outer_frame gegeben
            return getattr(self.outer_frame, item)
        else:
            # The remaining attributes (_w, children, etc.) will be handed
            # over to self.inner_frame
            return getattr(self.inner_frame, item)

    def create_outer_frame(self, master: tk.Frame) -> None:
        """
        Creates the outer frame and scrollbars.

        Args:
            master: The parent widget.
        """
        # Create outer frame
        self.outer_frame = tk.Frame(master, bg=self.color_scheme.app['accent1'])

        # Create vertical scrollbar
        if self.vscrl:
            self.vsb = ttk.Scrollbar(self.outer_frame, orient=tk.VERTICAL)
            self.vsb.grid(row=0, column=1, sticky='ns')

        # Create horizontal scrollbar
        if self.hscrl:
            self.hsb = ttk.Scrollbar(self.outer_frame, orient=tk.HORIZONTAL)
            self.hsb.grid(row=1, column=0, sticky='ew')

    def create_canvas(self) -> None:
        """
        Creates the canvas and connects it with the scrollbars.
        """
        # Create canvas at make it adjust to outer frame size
        self.canvas = tk.Canvas(self.outer_frame, highlightthickness=0,
                                width=self.width, height=self.height,
                                bg=self.color_scheme.app['accent1'])
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.outer_frame.rowconfigure(0, weight=1)
        self.outer_frame.columnconfigure(0, weight=1)

        # Connect scrollbars to canvas if applicable
        if self.vscrl:
            self.canvas['yscrollcommand'] = self.vsb.set
            self.vsb['command'] = self.canvas.yview

        if self.hscrl:
            self.canvas['xscrollcommand'] = self.hsb.set
            self.hsb['command'] = self.canvas.xview

        # Callbacks for mouse-enter and mouse-leave. The mouse will be bound to
        # the canvas if the cursor enters it and unbound if it leaves. This
        # allows multiples ScrollFrames to exist.
        self.canvas.bind('<Enter>', self.bind_mouse)
        self.canvas.bind('<Leave>', self.unbind_mouse)

    def create_inner_frame(self) -> None:
        """
        Create inner frame and place it inside the canvas.
        """
        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.inner_frame, anchor='nw')
        self.inner_frame.bind("<Configure>", self.inner_frame_configure)

        # Define attributes to be handed outside
        self.attr_outside = set(dir(tk.Widget))

    # noinspection PyUnusedLocal
    def inner_frame_configure(self, event: tk.Event | None = None) -> None:
        """
        Callback that is triggered when the size of the inner frame changes.
        Redefines the scroll area.

        Args:
            event: The event that triggered the callback.
        """
        # Geometry of the canvas
        x1, y1, x2, y2 = self.canvas.bbox("all")

        # Redefine scroll area depending on which scrollbars exist
        if self.vscrl and not self.hscrl:
            height = self.canvas.winfo_height()
            self.canvas.config(scrollregion=(0, 0, x2, max(y2, height)))
        elif self.hscrl and not self.vscrl:
            width = self.canvas.winfo_width()
            self.canvas.config(scrollregion=(0, 0, max(x2, width), y2))
        else:
            height = self.canvas.winfo_height()
            width = self.canvas.winfo_width()
            self.canvas.config(
                scrollregion=(0, 0, max(x2, width), max(y2, height)))

    # noinspection PyUnusedLocal
    def bind_mouse(self, event: tk.Event | None = None) -> None:
        """
        Bind callbacks for the mouse wheel

        Args:
            event: The event that triggered the callback.
        """
        self.canvas.bind_all('<4>', self.on_mousewheel)           # Linux
        self.canvas.bind_all('<5>', self.on_mousewheel)           # Linux
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)  # Mac/Windows

    # noinspection PyUnusedLocal
    def unbind_mouse(self, event=None) -> None:
        """
        Unbind callbacks for the mouse wheel.

        Args:
            event: The event that triggered the callback.
        """
        self.canvas.unbind_all('<4>')           # Linux
        self.canvas.unbind_all('<5>')           # Linux
        self.canvas.unbind_all('<MouseWheel>')  # Mac/Windows

    def on_mousewheel(self, event: tk.Event) -> None:
        """
        Callback for the mouse wheel.

        Args:
            event: The event that triggered the callback.
        """
        # Scroll vertical (mouse wheel) or horizontally (SHIFT + mouse wheel)?
        if event.state & 1:  # type: ignore
            scroll_function = self.canvas.xview_scroll

            # Cancel if there is no horizontal scrollbar
            if not self.hscrl:
                return
        else:
            scroll_function = self.canvas.yview_scroll

            # Cancel if there is no vertical scrollbar
            if not self.vscrl:
                return

        # Scroll (event.delta -> Mac/Windows, event.num -> Linux)
        if event.num == 4 or event.delta > 0:
            scroll_function(-1, 'units')
        elif event.num == 5 or event.delta < 0:
            scroll_function(1, 'units')
