"""
pylightlib.tk.FnButtonFrame
===========================

A module for managing customizable function key widgets (F1–F12) in a graphical
user interface using Tkinter.

This module defines two core classes: `FnKey` and `FnButtonFrame`.

- `FnKey` represents a configurable function key, which can take the form of a
  standard button, a switch, a dropdown menu, or a dial. Each key can be
  associated with a callback function and Tkinter variables to dynamically
  update the GUI state.

- `FnButtonFrame` is a container frame that organizes multiple `FnKey` instances
  in a grid layout, supporting modifier keys like ALT. It dynamically binds
  keys, handles interaction callbacks, and manages visual states of buttons
  and widgets.

This system allows developers to define flexible, user-triggered UI controls
for function key layouts commonly used in hardware control panels, dev tools, or
power-user applications.

"""

# Libs
from __future__ import annotations
from typing import Callable
import tkinter
import tkinter as tk

# PyLightFramework
from pylightlib.tk.FramedWidget import FramedWidget


class FnKey:
    """
    Represents a functional UI key, which can be a button, switch, dropdown
    or dial.

    This class provides factory methods to configure itself as a specific type
    of control element. Each type has its own properties and can be linked to
    actions (callbacks) and Tkinter variables for interaction in a GUI.

    Attributes
    ----------
    type : str
        Type of the control ('button', 'switch', 'dropdown', or 'dial').
    text : str
        Label or caption of the control.
    action : Callable or None
        Callback function to execute on interaction.
    is_on : bool
        Current state for a switch control.
    items : list[str]
        List of selectable entries for dropdowns and dials.
    string_var : tkinter.StringVar
        Variable for the selected item in dropdown or dial.
    boolean_var : tkinter.BooleanVar
        Variable representing switch state.
    """
    type: str
    text: str
    action: Callable | None
    is_on: bool
    items: list[str]
    string_var: tkinter.StringVar
    boolean_var: tkinter.BooleanVar

    def button(self, text: str, action: Callable) -> FnKey:
        """
        Creates a new instance of FnKey for a button.

        Parameters
        ----------
        text : str
            Label or caption of the button.
        action : Callable
            Callback function to execute on button press.

        Returns
        -------
        FnKey
            Instance of FnKey with button type.
        """
        self.type = 'button'
        self.text = text
        self.action = action
        return self

    def switch(self, text: str, action: Callable, bvar: tk.BooleanVar) -> FnKey:
        """
        Creates a new instance of FnKey for a switch button.

        Parameters
        ----------
        text : str
            Label or caption of the switch.
        action : Callable
            Callback function to execute on switch state change.
        bvar : tk.BooleanVar
            Boolean variable representing the switch.

        Returns
        -------
        FnKey
            Instance of FnKey with switch type.
        """
        self.type = 'switch'
        self.text = text
        self.action = action
        self.is_on = bvar.get()
        self.boolean_var = bvar
        return self

    def dropdown(self, text: str, action: Callable, dropdown_items: list[str],
                 svar: tkinter.StringVar) -> FnKey:
        """
        Creates a new instance of FnKey for a dropdown (option menu).

        Parameters
        ----------
        text : str
            Label or caption of the dropdown.
        action : Callable
            Callback function to execute on selection change.
        dropdown_items : list[str]
            List of selectable entries.
        svar : tkinter.StringVar
            String variable for the selected item.

        Returns
        -------
        FnKey
            Instance of FnKey with dropdown type.
        """
        self.type = 'dropdown'
        self.text = text
        self.action = action
        self.items = dropdown_items
        self.string_var = svar
        return self

    def dial(self, text: str, action: Callable, dial_items: list[str],
             svar: tkinter.StringVar) -> FnKey:
        """
        Creates a new instance of FnKey for a dial.

        Parameters
        ----------
        text : str
            Label or caption of the dial.
        action : Callable
            Callback function to execute on dial rotation.
        dial_items : list[str]
            List of selectable entries.
        svar : tkinter.StringVar
            String variable for the selected item.

        Returns
        -------
        FnKey
            Instance of FnKey with dial type.
        """
        self.type = 'dial'
        self.text = text
        self.action = action
        self.items = dial_items
        self.string_var = svar
        return self


class FnButtonFrame(tk.Frame):
    """
    A frame that dynamically creates and manages a grid of function keys
    (F1–F12) in the form of buttons, switches, dropdowns, or dials, based on
    provided configuration.

    The class supports modifier keys (e.g., ALT), allowing for multiple
    configurations of function keys. Each key can have a custom action and
    UI widget associated with it.

    Attributes
    ----------
    master_frm : tk.Frame
        The parent frame this widget is packed into.
    fnkeys : dict[str, dict[int, FnKey]]
        A nested dictionary mapping modifiers and function key numbers to FnKey instances.
    button_count : dict[str, int]
        A dictionary that holds the count of buttons for each modifier row.
    buttons : dict[str, FramedWidget]
        A dictionary holding all button widget instances.
    switches : dict[str, bool]
        Tracks the ON/OFF status of switch-type buttons.
    switch_labels : dict[str, tk.Label]
        Stores label widgets associated with switch buttons.
    option_menus : dict[str, FramedWidget]
        Stores option menu widgets for dropdown keys.
    dials : dict[str, list[str]]
        Stores dial values for dial-type keys.
    callbacks : dict[str, Callable | None]
        Stores the callback functions for each fn key.
    alt_is_pressed : bool
        Tracks whether the ALT key is currently held down.
    alt_is_pressed_with_fnkey : bool
        Indicates if ALT was pressed during an fn key press.
    """
    master_frm: tk.Frame
    fnkeys: dict[str, dict[int, FnKey]] = {}
    button_count: dict[str, int] = {}
    buttons: dict[str, FramedWidget] = {}
    switches: dict[str, bool] = {}
    switch_labels: dict[str, tk.Label] = {}
    option_menus: dict[str, FramedWidget] = {}
    dials: dict[str, list[str]] = {}
    callbacks: dict[str, Callable | None] = {}
    alt_is_pressed: bool = False
    alt_is_pressed_with_fnkey: bool = False


    def __init__(self, master: tk.Frame, fnkeys: dict[str, dict[int, FnKey]],
                 **kwargs):
        """
        Initializes this frame and create the widgets based on the given
        dictionary fnkeys.

        Parameters
        ----------
        master : tk.Frame
            The parent frame this widget is packed into.
        fnkeys : dict[str, dict[int, FnKey]]
            A nested dictionary mapping modifiers and function key numbers to FnKey instances.
        **kwargs
            Additional keyword arguments for the frame.
        """
        tk.Frame.__init__(self, master=master, **kwargs)
        self.fnkeys = fnkeys

        # Count the number of buttons of each row
        for modifier, fnkeyrow in fnkeys.items():
            self.button_count[modifier] = len(fnkeyrow)

        # Create widgets (buttons, switches, dropdowns, etc.)
        row_count = 0
        for modifier, fnkeyrow in fnkeys.items():
            # Only add bottom border if it's the last row
            if row_count == len(self.button_count) - 1:
                borderbottom = 1
            else:
                borderbottom = 0

            self.create_widgets(master=tk.Frame(master=self), modifier=modifier,
                                fnkeyrow=fnkeyrow, borderbottom=borderbottom) \
                .grid(row=row_count, column=0, sticky='nesw')
            row_count += 1

        # Stretch widget to full width of window
        self.columnconfigure(0, weight=1)

        # Bindings for fn keys
        for i in range(1, 13):
            fnr = f'F{i}'
            master.bind(f'<KeyPress-{fnr}>', self.key_pressed)
            master.bind(f'<KeyRelease-{fnr}>', self.key_released)

        # Bindings for modifier keys
        master.bind('<KeyPress-Alt_L>', self.alt_pressed)
        master.bind('<KeyPress-Alt_R>', self.alt_pressed)
        master.bind('<KeyRelease-Alt_L>', self.alt_released)
        master.bind('<KeyRelease-Alt_R>', self.alt_released)

    def create_widgets(self, master: tk.Frame, modifier: str,
                       fnkeyrow: dict[int, FnKey], borderbottom: int) \
            -> tk.Frame:
        """
        Creates the widgets for one row/modifier.

        Parameters
        ----------
        master : tk.Frame
            The parent frame this widget is packed into.
        modifier : str
            The modifier key (e.g., 'ALT').
        fnkeyrow : dict[int, FnKey]
            A dictionary mapping function key numbers to FnKey instances.
        borderbottom : int
            Flag indicating whether to add a bottom border.

        Returns
        -------
        tk.Frame
            The frame containing the created widgets.
        """
        # Loop dictionary 'fnkeyrow' and create widgets
        button_count = 0
        for fnr, fnkey in fnkeyrow.items():
            # Create string for the name of the fn key
            if modifier == '':
                fnr = f'F{str(fnr)}'                     # type: ignore
            else:
                fnr = f'{modifier.upper()}+F{str(fnr)}'  # type: ignore

            # Only add right border it's the last widget in the row
            if button_count == len(fnkeyrow) - 1:
                borderright = 1
            else:
                borderright = 0
            button_count += 1

            # Create kwargs dictionary for creating instance of FramedWidget
            kwargs = {'master': master, 'text': f'{fnr}: {fnkey.text}',
                      'borderbottom': borderbottom, 'borderright': borderright}

            # Add button type-specific arguments
            # noinspection PyUnusedLocal
            match fnkey.type:
                case 'switch':
                    kwargs.update({'widget': 'switch_button',
                                   'variable': fnkey.boolean_var})
                case 'dropdown':
                    kwargs.update({'widget': 'option_menu_with_label',
                                   'values': fnkey.items,
                                   'variable': fnkey.string_var})
                case 'dial':
                    kwargs.update({'widget': 'dial',
                                   'values': fnkey.items,
                                   'variable': fnkey.string_var})
                case _:
                    kwargs.update({'widget': 'button'})

            # Create widget and add to master
            wdg = FramedWidget(**kwargs)  # type: ignore
            wdg.grid(row=0, column=master.grid_size()[0], sticky='nesw')
            # noinspection PyCallingNonCallable
            wdg.bind('<ButtonRelease-1>', self.key_released)  # type: ignore

            # Expand widget
            master.columnconfigure(master.grid_size()[0] - 1, weight=1)

            # Make all columns of the grid have the same widths (uniform = any
            # name for the group)
            master.grid_columnconfigure(master.grid_size()[0] - 1, weight=1,
                                        uniform='a')

            # Button type-specific actions
            # noinspection PyUnusedLocal
            # TODO: remove this match-case and only use self.buttons dict
            match fnkey.type:
                case 'switch':
                    # Update dictionary for switches
                    self.switches.update({str(fnr): fnkey.is_on})
                case 'dropdown':
                    # Update dictionary for option menus
                    self.option_menus.update({str(fnr): wdg})
                case 'dial':
                    # Update dictionary for dials
                    self.dials.update({str(fnr): fnkey.items})
                case _:
                    pass

            # Update dictionaries for button instance and callback
            self.buttons.update({str(fnr): wdg})
            self.callbacks.update({str(fnr): fnkey.action})

        return master

    # noinspection PyUnusedLocal
    def alt_pressed(self, event: tk.Event) -> None:
        """
        Saves that the ALT key is pressed.

        Parameters
        ----------
        event : tk.Event
            The event object.
        """
        self.alt_is_pressed = True

    # noinspection PyUnusedLocal
    def alt_released(self, event: tk.Event) -> None:
        """
        Saves that the ALT key was released.

        Parameters
        ----------
        event : tk.Event
            The event object.
        """
        self.alt_is_pressed = False

    def key_pressed(self, event: tk.Event) -> None:
        """
        Callback that will be triggered when an fn key (F1-F12) is pressed.
        Changes the style of the corresponding button to pressed.

        Parameters
        ----------
        event : tk.Event
            The event object.
        """
        if self.alt_is_pressed is True:
            # ALT+FXX
            fnr = f'ALT+{event.keysym}'
            self.alt_is_pressed_with_fnkey = True
        else:
            # FXX
            fnr = event.keysym

        # Change button style to pressed
        self.buttons[fnr].wdg.configure(style='button_pressed.TLabel')  # type: ignore

    def key_released(self, event: tk.Event) -> None:
        """
        Callback that will be triggered when an fn key (F1-F12) is released.
        Depending on the button type one of the following actions will be
        performed:

        - 'button':   no button specific-action
        - 'switch':   change label to ON or OFF
        - 'dial':     change label to next value in items list
        - 'dropdown': open drop down

        After that the button style will be changed back to normal (!pressed)
        and the callback for the fn key will be run.

        Parameters
        ----------
        event : tk.Event
            The event object.
        """
        fnr = None
        modifier = ''

        # Triggered by mouse or keyboard?
        if event.keysym == '??':
            # Triggered by mouse -> fn number and modifier must be determined
            for key in self.buttons:
                if event.widget == self.buttons[key].wdg:
                    fnr = key
                    key_copy = key
                    if '+' in fnr:
                        modifier = key_copy.split('+')[0]
                    else:
                        modifier = ''
        else:
            # Triggered by keyboard
            fnr = event.keysym

            # ALT+FXX ?
            if self.alt_is_pressed or self.alt_is_pressed_with_fnkey:
                fnr = f'ALT+{fnr}'
                modifier = 'ALT'
                self.alt_is_pressed_with_fnkey = False

        # Determine button type
        fnr_int = int(str(fnr).replace('ALT+', '').replace('F', ''))
        button_type = self.fnkeys[modifier][fnr_int].type

        # Switch?
        # noinspection PyUnusedLocal
        match button_type:
            case 'switch':
                self.buttons[fnr].toggle_switch()  # type: ignore
            case 'dial':
                self.buttons[fnr].rotate_dial()    # type: ignore
            case 'dropdown':
                # Open dropdown
                self.option_menus[fnr].wdg.focus_set()      # type: ignore
                self.option_menus[fnr].wdg.event_generate(  # type: ignore
                    '<space>', when='head'
                )

                # Windows
                # TODO: check if event_generate also works on Windows, if yes
                #  the following 2 lines can be removed
                # shell = win32com.client.Dispatch('WScript.Shell')
                # shell.SendKeys(' ', 0)  # Leertasten-Druck simulieren
            case _:
                pass

        # Display button as not pressed
        self.buttons[fnr].wdg.configure(style='button.TLabel')  # type: ignore

        # Run callback if it exists for this button
        if self.callbacks[fnr] is not None:  # type: ignore
            self.callbacks[fnr]()            # type: ignore

            # thread = Thread(target=self.callbacks[fnr])
            # thread.start()

    def reset_button_state(self) -> None:
        """
        Display all buttons as not pressed.
        """
        for button in self.buttons.values():
            button.wdg.state(['!pressed', '!disabled'])  # type: ignore
