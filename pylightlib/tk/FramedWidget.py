"""
pylightlib.tk.FramedWidget
==========================

A customizable frame wrapper for standard Tkinter and ttk widgets with
configurable borders and focus-based highlighting.

This module provides the `FramedWidget` class, a versatile container for ttk
widgets like buttons, entries, labels, option menus, dials, and listboxes.

Tkinter does not natively support custom widget borders in a flexible way.
`FramedWidget` addresses this by embedding the desired widget inside a
`tk.Frame`, which acts as a colored and configurable border. The frame responds
to focus events and allows dynamic styling of widgets to reflect active/inactive
states.

In addition to standard widgets, `FramedWidget` supports:

- Switch buttons with ON/OFF logic and labels
- Dials that rotate through a list of values
- Option menus with optional labels
- Editable listboxes with drag-and-drop and scrollbar

It is designed to integrate easily into the PyLight GUI framework and
streamline consistent widget styling with extended behavior.

"""

# Libs
import tkinter as tk
import tkinter.ttk as ttk

# PyLightFramework
from pylightlib.tk.EditableListbox import EditableListbox


class FramedWidget(tk.Frame):
    """
    Despite the relief styles (FLAT, RAISED, SUNKEN, GROOVE and RIDGE) it is not
    possible to customize the border of Tkinter widgets.

    This class is a workaround for that. It inherits tk.Frame. A ttk widget (Label, Button,
    Entry, etc.) will is created and placed within the frame. The background of
    the frame is set to the desired border color, the padding of the ttk widget
    to the desired border width.

    Additionally, the border color changes when the widget gains focus.

    The following widgets are supported:

    - Button
    - Switch Button
    - Entry
    - Label
    - Option Menu
    - Option Menu with Label
    - Dial
    - Listbox

    Attributes
    ----------
    default_border_width : int
        Default border width in pixels.
    bordercolor : tuple[str]
        Color of the border around the widget (= background color of the frame).
    default_border_color : tuple[str, str]
        Default border color of the widget. Can be set from outside this class.
    wdg : object
        Instance of the widget within the frame (Button, Entry etc.).
    lbl : tk.Label
        Label in front of the widget (applicable for some widgets).
    frm : tk.Frame
        If the widget has a label in front of it both will be in this frame.
    boolean_var : bool
        ON/OFF status of a switch, if applicable.
    items : list[str]
        List of the items of a dial, if applicable.
    string_var : tk.StringVar
        String var for an option menu or a dial, if applicable.
    get : object
        Get method of the entry if applicable.
    insert : object
        Insert method of the entry if applicable.
    frm_bind : object
        Bind method of this frame (bind will be mapped to the bind method of the widget).
    frm_configure : object
        Configure method of this frame (configure will be mapped to the configure method of the widget).
    bind : object
        Bind method of the widget.
    configure : object
        Configure method of the widget.
    """
    default_border_width: int = 1
    bordercolor: tuple[str]
    default_border_color = ('black', 'black')
    wdg: object
    lbl: tk.Label
    frm: tk.Frame
    boolean_var: bool
    items: list[str] = []
    string_var: tk.StringVar
    get: object
    insert: object
    frm_bind: object
    frm_configure: object
    bind: object       # type: ignore
    configure: object  # type: ignore


    def __init__(self, master: object, widget: str, *args, **kwargs):
        """
        Creates the frame which functions as a border and the widget within it.

        Parameters
        ----------
        master : object
            Master widget which contains this frame.
        widget : str
            Widget type ('button', 'switch_button', 'entry', 'label',
            'option_menu', 'option_menu_with_lbl' or 'dial').
        *args
            Arguments for the widget.
        **kwargs
            Keyword arguments for the widget.
        """
        tk.Frame.__init__(self, master=master)  # type: ignore

        # Parse border color (create tuple if string is given)
        bordercolor = kwargs.pop('bordercolor', self.default_border_color)
        if type(bordercolor) is not tuple:
            self.bordercolor = (bordercolor, bordercolor)  # type: ignore
        else:
            self.bordercolor = bordercolor

        # Set border color and create widget within frame
        self.configure(background=self.bordercolor[0])  # type: ignore
        self.create_widget(widget, *args, **kwargs)

    def create_widget(self, widget: str, *args, **kwargs) -> None:
        """
        Creates a widget (button, entry, etc.) depending on the argument widget and packs it within this frame.

        Possible kwargs: borderleft, borderright, borderttop, borderbottom

        Parameters
        ----------
        widget : str
            Widget type ('button', 'switch_button', 'entry', 'label',
            'option_menu', 'option_menu_with_lbl' or 'dial').
        *args
            Arguments for the widget.
        **kwargs
            Keyword arguments for the widget.
        """
        # Get border thickness from kwargs and create tuples for padx and pady
        borderleft   = kwargs.pop('borderleft', self.default_border_width)
        borderright  = kwargs.pop('borderright', self.default_border_width)
        bordertop    = kwargs.pop('bordertop', self.default_border_width)
        borderbottom = kwargs.pop('borderbottom', self.default_border_width)
        padx = (borderleft, borderright)
        pady = (bordertop, borderbottom)

        # Create widget
        switcher = {
            'button': self.button,
            'switch_button': self.switch_button,
            'entry': self.entry,
            'label': self.label,
            'option_menu': self.option_menu,
            'option_menu_with_label': self.option_menu_with_label,
            'dial': self.dial,
            'listbox': self.listbox
        }
        func = switcher.get(widget, lambda: f'Widget {widget} not supported!')
        wdg = func(*args, **kwargs)  # type: ignore

        # Get the object of the widget and if applicable get the object of the
        # label and the frame the label and widget are packed in
        if type(wdg) is tuple:
            pack_wdg = wdg[0]  # Frame that contains label and widget
            self.lbl = wdg[1]  # Label
            self.wdg = wdg[2]  # Widget
        else:
            pack_wdg = wdg
            self.wdg = wdg

        # Remap bind and configure
        self.frm_bind = self.bind
        self.frm_configure = self.configure
        self.bind = self.wdg.bind  # type: ignore
        self.configure = self.wdg.configure  # type: ignore

        # Pack widget into this frame
        pack_wdg.pack(fill='both', expand=1, padx=padx, pady=pady, ipady=4)

    def toggle_border_color(self, e: tk.Event) -> None:
        """
        Callback for FocusIn and FocusOut event.

        Parameters
        ----------
        e : tk.Event
            Event object.
        """
        if self['background'] == self.bordercolor[1]:    # type: ignore
            self.config(background=self.bordercolor[0])  # type: ignore
        else:
            self.config(background=self.bordercolor[1])  # type: ignore

    def button(self, *args, **kwargs) -> ttk.Button:
        """
        Returns an instance of ttk.Button.

        Parameters
        ----------
        *args
            Arguments for the button.
        **kwargs
            Keyword arguments for the button.

        Returns
        -------
        ttk.Button
            Instance of ttk.Button.
        """
        master = kwargs.pop('master', self)
        btn = ttk.Button(master=master, *args, **kwargs, style='button.TLabel')  # type: ignore

        # Add whitespaces around the button text (the argument ipadx of the
        # .pack method won't work because a style is used for the buttion)
        btn['text'] = '  ' + btn['text'] + '  '

        return btn

    def entry(self, *args, **kwargs) -> ttk.Entry:
        """
        Returns an instance of ttk.Entry.

        Parameters
        ----------
        *args
            Arguments for the entry.
        **kwargs
            Keyword arguments for the entry.

        Returns
        -------
        ttk.Entry
            Instance of ttk.Entry.
        """
        master = kwargs.pop('master', self)
        # entry = ttk.Entry(master=master, *args, **kwargs, style='entry.TLabel')
        entry = ttk.Entry(master=master, *args, **kwargs, style='entry.TEntry')  # type: ignore

        # Bindings, so that the entry gets highlighted when it gains focus
        entry.bind('<FocusIn>', self.toggle_border_color)
        entry.bind('<FocusOut>', self.toggle_border_color)

        self.get = entry.get
        self.insert = entry.insert

        return entry

    def label(self, *args, **kwargs) -> ttk.Label:
        """
        Returns an instance of ttk.Label.

        Parameters
        ----------
        *args
            Arguments for the label.
        **kwargs
            Keyword arguments for the label.

        Returns
        -------
        ttk.Label
            Instance of ttk.Label.
        """
        master = kwargs.pop('master', self)
        label = ttk.Label(master=master, *args, **kwargs, style='button.TLabel')  # type: ignore

        return label

    def option_menu(self, **kwargs) -> ttk.OptionMenu:
        """
        Returns an instance of ttk.OptionMenu.

        Parameters
        ----------
        **kwargs
            Keyword arguments for the option menu.

        Returns
        -------
        ttk.OptionMenu
            Instance of ttk.OptionMenu.
        """
        master = kwargs.pop('master', self)
        self.string_var: tk.StringVar = kwargs.pop('variable')
        self.items: list[str] = kwargs.pop('values')

        om = ttk.OptionMenu(master, self.string_var, self.string_var.get(),
                            *self.items, style='button.TLabel', **kwargs)

        return om

    def option_menu_with_label(self, **kwargs) \
        -> tuple[ttk.Frame, ttk.Label, ttk.OptionMenu]:
        """
        Creates a frame and packs a label and an option menu in it.

        Parameters
        ----------
        **kwargs
            Keyword arguments for the option menu.

        Returns
        -------
        tuple[ttk.Frame, ttk.Label, ttk.OptionMenu]
            Tuple of instances: (Frame, Label, OptionMenu).
        """
        lbl_text = kwargs.pop('text')

        # Frame
        frm = ttk.Frame(master=self)

        # Label
        lbl = ttk.Label(master=frm, text=lbl_text, style='button.TLabel')
        lbl.pack(side='left', fill='both')

        # Option Menu
        om = self.option_menu(master=frm, **kwargs)
        om.pack(side='left', fill='both', expand=1, ipadx=33)

        return frm, lbl, om

    def switch_button(self, **kwargs) \
        -> tuple[ttk.Frame, ttk.Label, ttk.Button]:
        """
        Creates a frame and packs a label and a switch button in it.

        Parameters
        ----------
        **kwargs
            Keyword arguments for the switch button.

        Returns
        -------
        tuple[ttk.Frame, ttk.Label, ttk.Button]
            Tuple of instances: (Frame, Label, Button).
        """
        self.boolean_var: tk.BooleanVar = kwargs.pop('variable')

        # Frame
        frm = ttk.Frame(master=self, style='button.TLabel')

        # Label-Frame
        lbl_frm = ttk.Frame(master=frm, style='button.TLabel')
        lbl_frm.pack(side='left', fill='both')

        # Label
        lbl = ttk.Label(master=lbl_frm, width=3, anchor='c', justify=tk.CENTER)  # type: ignore
        lbl.pack(side='left', padx=(5,5))

        # Set style and text of the label depending on ON/OFF status
        if self.boolean_var.get():  # type: ignore
            lbl.config(text='ON', style='switch_button_label_on.TLabel')
        else:
            lbl.config(text='OFF', style='switch_button_label_off.TLabel')

        # Button
        btn = self.button(**kwargs, master=frm)
        btn.pack(side='right', fill='both', expand=1)

        return frm, lbl, btn

    def dial(self, **kwargs) -> tuple[ttk.Frame, ttk.Label, ttk.Button]:
        """
        Creates a frame and packs a label and dial in it.

        Parameters
        ----------
        **kwargs
            Keyword arguments for the dial.

        Returns
        -------
        tuple[ttk.Frame, ttk.Label, ttk.Button]
            Tuple of instances: (Frame, Label, Button).
        """
        self.string_var: tk.StringVar = kwargs.pop('variable')
        self.items: list[str] = kwargs.pop('values')
        lbl_text = kwargs.pop('text')

        # Calculate label width = length of longest item
        width = 0
        for item in self.items:
            if len(item) > width:
                width = len(item)

        # Frame
        frm = ttk.Frame(master=self)

        # Label-Frame
        lbl_frm = ttk.Frame(master=frm, style='button.TLabel')
        lbl_frm.pack(side='left', fill='both')

        # Label
        lbl = ttk.Label(master=lbl_frm, text=self.string_var.get(),
                        width=width+1, anchor='c', justify=tk.CENTER,  # type: ignore
                        style='dial_button_label.TLabel')
        lbl.pack(side='left', padx=(5,5))

        # Button
        btn = self.button(**kwargs, master=frm, text=lbl_text)
        btn.pack(side='right', fill='both', expand=1)

        return frm, lbl, btn

    def toggle_switch(self) -> None:
        """
        Sets the label of a switch to ON/OFF and changes the style of the label.

        The switch is controlled by a boolean var.

        The label of the switch is set to 'ON' if the boolean var is True and to
        'OFF' if the boolean var is False. The style of the label is set to
        'switch_button_label_on.TLabel' if the boolean var is True and to
        'switch_button_label_off.TLabel' if the boolean var is False.
        """
        if self.boolean_var.get():  # type: ignore
            self.lbl.config(text='OFF', style='switch_button_label_off.TLabel')  # type: ignore
            self.boolean_var.set(False)  # type: ignore
        else:
            self.lbl.config(text='ON', style='switch_button_label_on.TLabel')  # type: ignore
            self.boolean_var.set(True)  # type: ignore

    def rotate_dial(self) -> None:
        """
        Rotates the dial (= switch to the next value in the item list).
        """
        # Get current index
        cur_index = self.items.index(self.lbl['text'])

        # Get next index
        if cur_index == len(self.items) - 1:
            next_index = 0
        else:
            next_index = cur_index + 1

        # Set dial (= set label text and string var)
        self.lbl['text'] = self.items[next_index]
        self.string_var.set(self.items[next_index])

    def listbox_no_padding(self, *args, **kwargs) -> EditableListbox:
        """
        Returns an instance of EditableListbox().

        Parameters
        ----------
        *args
            Arguments for the listbox.
        **kwargs
            Keyword arguments for the listbox.

        Returns
        -------
        EditableListbox
            Instance of EditableListbox.
        """
        lbox = EditableListbox(master=self, relief='flat', *args, **kwargs)  # type: ignore

        # Add scrollbar
        vsb = ttk.Scrollbar(master=self, orient='vertical', command=lbox.yview,
                            style='Vertical.TScrollbar')
        lbox.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')

        # Bindings, so that the entry gets highlighted when it gains focus
        lbox.bind('<FocusIn>', self.toggle_border_color)
        lbox.bind('<FocusOut>', self.toggle_border_color)

        self.append = lbox.append
        self.move_selected_item = lbox.move_selected_item

        return lbox

    def listbox(self, *args, **kwargs) \
        -> tuple[ttk.Frame, ttk.Frame, EditableListbox]:
        """
        Returns an instance of EditableListbox().

        Parameters
        ----------
        *args
            Arguments for the listbox.
        **kwargs
            Keyword arguments for the listbox.

        Returns
        -------
        tuple[ttk.Frame, ttk.Frame, EditableListbox]
            Tuple of instances: (Frame, Frame, EditableListbox).
        """
        # Frame to be able to add padding
        frm = ttk.Frame(master=self, style='light_button.TLabel')

        # Listbox
        lbox = EditableListbox(master=frm, relief='flat', *args, **kwargs)  # type: ignore
        lbox.pack(side='left', fill='both', padx=5, pady=5)

        # Add scrollbar
        vsb = ttk.Scrollbar(master=frm, orient='vertical', command=lbox.yview,
                            style='Vertical.TScrollbar')
        lbox.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')

        # Bindings, so that the entry gets highlighted when it gains focus
        lbox.bind('<FocusIn>', self.toggle_border_color)
        lbox.bind('<FocusOut>', self.toggle_border_color)

        self.append = lbox.append
        self.move_selected_item = lbox.move_selected_item

        return frm, frm, lbox
