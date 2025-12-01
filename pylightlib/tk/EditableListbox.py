"""
pylightlib.tk.EditableListbox
=============================

A custom Tkinter Listbox widget with inline editing functionality.

This module provides the `EditableListbox` class, which extends the standard
`tkinter.Listbox` widget to support editing of list items directly within the
Listbox. Items can be edited by double-clicking or pressing the Return key, and
also by typing a character while the Listbox is focused. It also allows for
simple item reordering and includes special handling for German umlaut key
mappings.

Key features include:

- Inline editing of items using an Entry widget
- Keyboard or mouse-triggered editing
- Customizable foreground/background colors for items and the edit Entry
- Reordering of items via method calls
- Partial support for German special characters (umlauts)
- Support for both string and numeric entry initialization

This widget is useful in GUI applications that require interactive list
management, such as task lists, configuration editors, or playlist managers.

"""

import string
import tkinter as tk


class EditableListbox(tk.Listbox):
    """
    This class inherits tkinter.Listbox and adds functionality to edit list box items by double-clicking or pressing enter.

    Attributes
    ----------
    selected_index : int
        Index of the currently selected item.
    read_only : bool
        Indicates of the listbox is read-only.
    moved_item_index : int or None
        Index of the last moved listbox item.
    moved_item_amount : int or None
        Amount the last moved item was moved by.
    item_bg : str or None
        Background color of the listbox item.
    item_fg : str or None
        Foreground color of the listbox item.
    entry_fg : str or None
        Foreground color of the entry for editing a listbox item.
    entry_bg : str or None
        Background color of the entry for editing a listbox item.
    UMLAUTS : dict
        Dictionaries with the key names of umlauts.
    """
    selected_index: int
    read_only: bool
    moved_item_index: int | None = None
    moved_item_amount: int | None = None
    item_bg: str | None = None
    item_fg: str | None = None
    entry_fg: str | None = None
    entry_bg: str | None = None
    UMLAUTS = {'Key-adiaeresis': 'ä',
               'Key-odiaeresis': 'ö',
               'Key-udiaeresis': 'ü'}
    """Dictionaries with the key names of umlauts."""

    # TODO: add possibility to select and move multiple items at once

    def __init__(self, master: tk.Frame, **kwargs):
        """
        Sets callbacks for double click and enter key.

        Parameters
        ----------
        master : tk.Frame
            Parent widget.
        **kwargs
            Arbitrary keyword arguments.
        """
        super().__init__(master, **kwargs)

        # Create list of the alphabet
        azAZ09 = list(string.ascii_letters)

        # Add numbers 0-9 and keypad number 0-9
        numbers = list(range(0, 10))
        azAZ09 += [f'Key-{str(i)}' for i in numbers]
        azAZ09 += [f'KP_{str(i)}' for i in numbers]

        # Add umlauts
        azAZ09 += list(self.UMLAUTS.keys())

        # Add =
        azAZ09.append('=')

        # Start editing by typing any letter (a-z) or number (0-9) on the
        # keyboard
        for char in azAZ09:
            self.bind(f'<{char}>', lambda event, arg=str(char):  # type: ignore
                      self.start_editing(event, arg))

        # Start Editing by double-clicking or pressing return
        self.bind('<Double-1>', self.start_editing)
        self.bind('<Return>', self.start_editing)
        self.bind('<KP_Enter>', self.start_editing)


    def append(self, items: object) -> None:
        """
        Adds a new item at the bottom of the list box.

        Parameters
        ----------
        items : object
            Item or list of items to be added (will be converted to str).
        """
        # If a string is given create a list with one element
        if not isinstance(items, list):
            items = [items]

        # Convert items to string and add to listbox
        for item in items:
            self.insert('end', str(item))

    def start_editing(self, event: tk.Event,
                      first_character: str | None = None) -> None:
        """
        Callback for editing an item.

        Creates an entry and places it over the listbox item.

        Parameters
        ----------
        event : tk.Event
            Event object.
        first_character : str or None, optional
            Character the callback was triggered by.
        """
        # End function call if listbox is readonly
        if self.read_only:
            return

        # Get index and text of selected item
        if len(event.widget.curselection()) > 0:
            self.selected_index = event.widget.curselection()[0]
        else:
            self.selected_index = 0
        text = self.get(self.selected_index)

        # y-position of the item (for entry position)
        y0 = self.bbox(self.selected_index)[1]  # type: ignore

        # Create entry
        entry = tk.Entry(self, borderwidth=0, highlightthickness=0,
                         relief='flat')

        # Was the callback triggered by pressing a letter or number on keyboard?
        if first_character is not None:
            # Yes, set entry text to character the callback was triggered by
            first_character = first_character.replace('Key-', '')
            first_character = first_character.replace('KP_', '')

            for key_name, umlaut in self.UMLAUTS.items():
                first_character = first_character.replace(key_name, umlaut)

            entry.insert(0, first_character)
        else:
            # No it was triggered by pressing enter or double-clicking
            # Set entry text to listbox item and select all
            entry.insert(0, text)
            entry.selection_from(0)
            entry.selection_to('end')

        # Save fore and background color of the listbox item
        self.item_bg = self.itemcget(self.selected_index, 'bg')
        self.item_fg = self.itemcget(self.selected_index, 'fg')

        # Set font, foreground and background of the entry
        entry.configure(font=self.cget('font'))

        if self.entry_fg:
            entry.configure(fg=self.entry_fg)
        else:
            entry.configure(fg=self.cget('selectforeground'))

        if self.entry_bg:
            entry.configure(bg=self.entry_bg)
        else:
            entry.configure(bg=self.cget('selectbackground'))

        # Bind callbacks
        entry.bind('<Return>', self.accept_editing)
        entry.bind('<KP_Enter>', self.accept_editing)
        entry.bind('<Escape>', self.cancel_editing)
        entry.bind('<Tab>', self.cancel_editing)
        entry.bind('<Button-1>', self.cancel_editing)

        # Place the entry over the listbox item and set focus
        entry.place(relx=0, y=y0, relwidth=1, width=0)
        entry.focus_set()
        entry.grab_set()

    def cancel_editing(self, event: tk.Event) -> None:
        """
        Callback for canceling the editing of a listbox item.

        Destroy the entry and re-select the listbox item.

        Parameters
        ----------
        event : tk.Event
            Event object.
        """
        # Destroy entry
        event.widget.destroy()

        # Select listbox item
        self.select_set(self.selected_index)
        self.event_generate('<<ListboxSelect>>')
        self.focus_set()

    def accept_editing(self, event: tk.Event):
        """
        Callback for saving the edited listbox item.

        Parameters
        ----------
        event : tk.Event
            Event object.
        """
        # Delete old item, insert new text at same position and destroy entry
        new_text = event.widget.get()
        self.delete(self.selected_index)
        self.insert(self.selected_index, new_text)
        event.widget.destroy()

        # Select edited item
        self.select_item(self.selected_index)
        self.event_generate('<<ItemUpdate>>')

        # Restore the fore and background color of the listbox item
        self.itemconfig(self.selected_index, bg=self.item_bg)
        self.itemconfig(self.selected_index, fg=self.item_fg)

    def select_item(self, index: int, generate_event: bool = True):
        """
        Selects an item by index.

        Parameters
        ----------
        index : int
            Index of the item to be selected.
        generate_event : bool, optional
            Generate a selection event.
        """
        # Clear selection
        self.selection_clear(0, 'end')

        # Select item
        self.select_set(index)
        self.activate(index)
        self.focus_set()

        # Generate event
        if generate_event:
            self.event_generate('<<ListboxSelect>>')

    def move_selected_item(self, amount: int):
        """
        Moves the selected item by the given amount.

        Parameters
        ----------
        amount : int
            Amount the item should be moved by.
        """
        selected_index = self.get_selected_index()

        # Calculate new index
        if amount < 0 and selected_index == 0:
            return
        elif amount > 0 and selected_index == self.size() - 1:
            return
        else:
            new_index = selected_index + amount

        # Save selected item, delete from listbox and insert at new index
        item = self.get(selected_index)
        self.delete(selected_index)
        self.insert(new_index, item)
        self.select_item(new_index)

        # Save new index and amount
        self.moved_item_index = new_index
        self.moved_item_amount = amount

        # Scroll ListBox if the moved item is not visible anymore
        self.see(self.get_selected_index())

    def get_selected_index(self) -> int | bool:
        """
        Returns the index of the currently selected item.

        Returns
        -------
        int or bool
            Index of the selected item or False if no item is selected.
        """
        selection = self.curselection()

        if selection:
            return selection[0]
        else:
            return False
