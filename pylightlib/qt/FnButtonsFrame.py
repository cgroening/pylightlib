"""
pylightlib.qt.FnButtonsFrame
============================

Function key bar with modifier support (child of QFrame)

Author:
    Corvin Gröning

Date:
    2025-03-04

Version:
    0.9

This module defines a function key bar that visually represents function keys
(F1-F12) as buttons, optionally grouped by keyboard modifiers (None, ALT, CTRL
and SHIFT). Each button executes the same function as the corresponding function
key on the keyboard.

The function key bar dynamically generates rows for each modifier, ensuring
that function keys with different modifiers (e.g., ALT+F1, CTRL+F2) are
displayed separately.

+-----------------------------------------------------------+
|  [F1]  [F2]  [F3]  ...  [F12]          (No modifier row)  |
+-----------------------------------------------------------+
|  [ALT+F1]  [ALT+F2]  [ALT+F3]  ...  [ALT+F12]  (ALT row)  |
+-----------------------------------------------------------+
|  [CTRL+F1] [CTRL+F2] [CTRL+F3] ... [CTRL+F12] (CTRL row)  |
+-----------------------------------------------------------+
|  [SHIFT+F1] [SHIFT+F2] ... [SHIFT+F12]       (SHIFT row)  |
+-----------------------------------------------------------+

Each function key button supports different interaction types:
- **Button:**   A standard pressable button.
- **Toggle:**   A switch-like button that stays on/off.
- **Dropdown:** A combo box for selecting an option.

When a function key (or its corresponding button) is pressed, its assigned
action is executed.

Usage:
------
1. Instantiate `FnButtonsFrame` in a Qt application.
2. Define function keys actions using `FnKeyDefinition`.
3. Use the function key bar for interaction.

"""

from __future__ import annotations
from enum import Enum, auto
from collections import defaultdict
from typing import Any, Callable
import contextlib

# == Qt imports (use external folder when app is bundled for LGPL conformity) ==
from pylightlib.msc.SysPathHandler import SysPathHandler


SysPathHandler().set_new_sys_path()
try:
    from PySide6 import QtCore, QtWidgets                             # type: ignore # noqa
    from PySide6.QtCore import Qt                                     # type: ignore # noqa
    from PySide6.QtGui import QKeyEvent                               # type: ignore # noqa
    from PySide6.QtWidgets import (QFrame, QHBoxLayout, QPushButton,  # type: ignore # noqa
                                   QComboBox, QVBoxLayout, QLabel)    # type: ignore # noqa
except ImportError as e:
    print(f'Import Error ({__file__}):\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()


class Modifier(Enum):
    """
    Enumeration for keyboard modifiers.

    This class represents different modifier keys that can be used in
    combination with the function keys, such as ALT, CTRL, and SHIFT.
    """
    NONE = None
    ALT = 'ALT'
    CTRL = 'CTRL'
    SHIFT = 'SHIFT'


class FnKey(Enum):
    """
    Enumeration for function keys.

    This class represents the standard function keys (F1–F12) typically found
    on a standard keyboard.
    """
    F1 = 'F1'
    F2 = 'F2'
    F3 = 'F3'
    F4 = 'F4'
    F5 = 'F5'
    F6 = 'F6'
    F7 = 'F7'
    F8 = 'F8'
    F9 = 'F9'
    F10 = 'F10'
    F11 = 'F11'
    F12 = 'F12'


class FnKeyType(Enum):
    """
    Enumeration for widget types for the function key bar.
    """
    button = auto()
    toggle = auto()
    dropdown = auto()


class FnKeyDefinition:
    """
    Defines a function key configuration.

    This class represents the definition of a function key (F1–F12) along with
    an optional modifier (ALT, CTRL, SHIFT). It provides attributes to store
    metadata such as captions, tooltips, and actions, as well as support for
    different widget types (button, toggle, dropdown).

    Attributes:
        fnkey:    FnKey.F1 to FnKey.F12.
        modifier: Modifier.NONE, Modifier.ALT, Modifier.CTRL or Modifier.SHIFT.
        widget_type: FnKeyType.button, FnKeyType.toggle oder FnKeyType.dropdown.
        caption: Text of the button.
        tooltip: Description of the function that is displayed on mouse over.
        action:  Reference to the function that will be called when the user
                 clicks on the widget or presses the fn key.
        is_on:   Indicates if the toggle is on.
        items:   Dictionary with the items for the dropdown:
                 {key: 'value'} or {'key': 'value'}
        current_item_index: The index of the currently selected item of the
                            dropdown.
    """
    fnkey: FnKey
    modifier: Modifier
    widget_type: FnKeyType
    caption: str
    tooltip: str
    action: Callable
    is_on: bool
    items: dict[Any, str]
    current_item_index: str


    def button(self, fnkey: FnKey, modifier: Modifier, caption: str,
               tooltip: str, action: Any) -> FnKeyDefinition:
        """
        Defines a button.

        Args:
            fnkey:    FnKey.F1 to FnKey.F12.
            modifier: Modifier.NONE, Modifier.ALT, Modifier.CTRL
                      or Modifier.SHIFT.
            caption:  Text on the button.
            tooltip:  Tooltip that is displayed on mouseover.
            action:   Action that is called when the button is clicked or the
                      corresponding function key is pressed.

        Returns:
            Instance of FnKeyDefinition.
        """
        self.fnkey = fnkey
        self.modifier = modifier
        self.widget_type = FnKeyType.button
        self.caption = caption
        self.tooltip = tooltip
        self.action = action
        return self

    def toggle(self, fnkey: FnKey, modifier: Modifier, caption: str,
               tooltip: str, action: Any, is_on: bool = False)  \
            -> FnKeyDefinition:
        """
        Defines a toggle/switch that can be on (True) or off (False).

        Args:
            fnkey:    FnKey.F1 to FnKey.F12.
            modifier: Modifier.NONE, Modifier.ALT, Modifier.CTRL
                      or Modifier.SHIFT.
            caption:  Text on the button.
            tooltip:  Tooltip that is displayed on mouseover.
            action:   Action that is called when the button is clicked or the
                      corresponding function key is pressed.
            is_on:    Indicates if the toggle/switch is on or off.

        Returns:
            Instance of FnKeyDefinition.
        """
        self.fnkey = fnkey
        self.modifier = modifier
        self.widget_type = FnKeyType.toggle
        self.caption = caption
        self.tooltip = tooltip
        self.action = action
        self.is_on = is_on
        return self

    def dropdown(self, fnkey: FnKey, modifier: Modifier, caption: str,
                 tooltip: str, action: Any, items: dict[Any, str],
                 current_item_index: Any) -> FnKeyDefinition:
        """
        Defines a dropdown.

        Args:
            fnkey:    FnKey.F1 to FnKey.F12.
            modifier: Modifier.NONE, Modifier.ALT, Modifier.CTRL
                      or Modifier.SHIFT.
            caption:  Text on the button.
            tooltip:  Tooltip that is displayed on mouseover.
            action:   Action that is called when the button is clicked or the
                      corresponding function key is pressed.
            items:    Dictionary with the items for the dropdown; the key can
                      be a string or integer.
            current_item_index: The index/key of the currently selected item.

        Returns:
            Instance of FnKeyDefinition.
        """
        self.fnkey = fnkey
        self.modifier = modifier
        self.widget_type = FnKeyType.dropdown
        self.caption = caption
        self.tooltip = tooltip
        self.action = action
        self.items = items
        self.current_item_index = current_item_index
        return self

    def get_key_combo(self) -> str:
        """
        Returns the key combination as string.

        Returns:
            "Modifier+FXX" oder "FXX" if modifier is NONE.
        """
        combo = self.fnkey.value

        if self.modifier != Modifier.NONE:
            combo = self.modifier.value + "+" + combo

        return combo


class FnButtonsFrame(QFrame):
    """
    Frame which contains buttons captioned with "FXX [funktion_description]".
    These buttons call the same action as the corresponding fn key.

    Attributes:
        parent_frame: Frame which contains this one.
        vertical_layout:  Instance of the vertical layout of this frame.
        fnkeys_list:  An unsorted list of FnKeyDefinition instances.
        compact_mode: Indicates if the fn key bar is in compact mode (button
                      text in only one row) or not (button text in two rows).
        fnkey_definitions: Dictionary with a sorted list of FnKeyDefinition
                           instances for each modifier.
        fnkey_definitions_by_key: Dictionary with the fn key as key and the
                                  FnKeyDefinition instance as value.
        widgets:     Dictionary containing all widgets:
                     {'Modifier+FXX': widget_instance}.
        slots:       Dictionary containing all slots
                     {'Modifier+FXX': slot_reference}.
        alt_pressed: Indicates if the ALT/Option key is currently pressed.
        fn_pressed:  Indicates if a fn key is currently pressed.
        simulate_alt_press: Indicates if a held down ALT/Option key shall be
                            simulated.
        func_text_separator: Separator for the function text in the button
                             caption (e.g., ' ' or '\n').
    """
    parent_frame: QFrame
    vertical_layout: QVBoxLayout
    fnkeys_list: list[FnKeyDefinition]
    compact_mode: bool
    fnkey_definitions: dict[str, list[FnKeyDefinition]]
    fnkey_definitions_by_key: dict[str, FnKeyDefinition]
    widgets: dict[str, Any]
    slots: dict[str, Any]
    alt_pressed: bool = False
    fn_pressed: bool = False
    simulate_alt_press: bool = False
    func_text_separator: str


    def __init__(self, qt_window: QtWidgets.QMainWindow, parent_frame: QFrame,
                 fnkeys_list: list[FnKeyDefinition], compact_mode: bool = True,
                 *args, **kwargs):
        """
        Creates the grid layout and widgets. Connects signal and slot for each
        fn key.

        Args:
            qt_window
            parent_frame
            fnkeys
            alt_fnkeys
            compact_mode
            *args
            **kwargs
        """
        super().__init__(parent_frame, *args, **kwargs)
        self.parent_frame = parent_frame
        self.fnkeys_list = fnkeys_list
        self.compact_mode = compact_mode

        # Set separator for function text in button caption
        self.func_text_separator = ' ' if compact_mode else '\n'

        # Create vertical layout
        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.setSpacing(2.5)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

        # Create widgets (buttons, switches, dropdowns)
        self.sort_and_group_fnkeys()
        self.fnkey_definitions_by_key = {}
        self.widgets = {}
        self.slots = {}

        for modifier in self.fnkey_definitions.keys():
            self.create_widget_row(self.fnkey_definitions[modifier])

        # Disconnect any slots from key press/release events within main window.
        # This is necessary if the app uses tabs with individual fn bars!
        with contextlib.redirect_stderr(None):  # Prevent warning in console
            try:
                # Disconnect existing slots
                # noinspection PyUnresolvedReferences
                qt_window.key_pressed.disconnect()
                # noinspection PyUnresolvedReferences
                qt_window.key_released.disconnect()
            except RuntimeError as error:
                print(error)

        # Connect signal and slot for key press/release within main window
        # noinspection PyUnresolvedReferences
        qt_window.key_pressed.connect(self.key_pressed)
        # noinspection PyUnresolvedReferences
        qt_window.key_released.connect(self.key_released)

        # Add self to parent frame
        self.parent_frame.layout().addWidget(self)

    def sort_and_group_fnkeys(self) -> None:
        """
        Sorts the fn key definitions by the fn key in ascending order and groups
        it by the modifier. The result is saved in self.fnkey_definitions.
        """
        # Sort the list by the fn key in ascending order
        sorted_list = sorted(
            self.fnkeys_list, key=lambda x: list(FnKey).index(x.fnkey)
        )

        # Create a dictionary which groups the fn keys by the modifier
        grouped_dict = defaultdict(list)
        for item in sorted_list:
            grouped_dict[item.modifier.name].append(item)

        self.fnkey_definitions = dict(grouped_dict)

    def key_pressed(self, event: QKeyEvent) -> None:
        """
        Slot that is run when a key is pressed. If it's a fn key the
        corresponding button will be displayed as pressed.

        Args:
            event
        """
        # Key == ALT ?
        if event.key() == QtCore.Qt.Key.Key_Alt:
            self.alt_pressed = True
        else:
            # Check if a fn key is pressed
            fnkey = self.fnkey_str(event, self.alt_pressed)
            if fnkey is not None:
                # Button/switch or dropdown?
                if fnkey in self.widgets:
                    if isinstance(self.widgets[fnkey], QPushButton):
                        self.fn_pressed = True
                        self.widgets[fnkey].setDown(True)

    def key_released(self, event: QKeyEvent) -> None:
        """
        Slot that is run when a key is released. If it's a function key the
        corresponding button will not be displayed as pressed anymore.
        The function for the fn key will be run.

        Args:
            event
        """
        # Determine fn key
        fnkey = self.fnkey_str(event, self.alt_pressed)
        if fnkey is not None:
            if fnkey in self.widgets:
                # Type == button/switch?
                if (self.fnkey_definitions_by_key[fnkey].widget_type
                        == FnKeyType.button
                    or self.fnkey_definitions_by_key[fnkey].widget_type
                        == FnKeyType.toggle):
                    # Toggle switch if applicable
                    if self.widgets[fnkey].isCheckable():
                        if self.widgets[fnkey].isChecked():
                            self.widgets[fnkey].setChecked(False)
                        else:
                            self.widgets[fnkey].setChecked(True)

                    # Don't show as pressed anymore
                    self.widgets[fnkey].setDown(False)

                    # Run slot
                    if self.slots[fnkey] is not None:
                        self.slots[fnkey]()
                    self.fn_pressed = False
                elif (self.fnkey_definitions_by_key[fnkey].widget_type
                      == FnKeyType.dropdown):
                    # Combobox öffnen
                    self.widgets[fnkey].showPopup()

        # Key == ALT ?
        if event.key() == QtCore.Qt.Key.Key_Alt:
            # Store the not-pressed status
            self.alt_pressed = False

            # If the user releases the ALT key while pressing down an F key,
            # the next time this method is called, it should behave as if the
            # ALT key is still pressed. When the user releases the F key, the
            # corresponding ALT+FXX function is executed.
            if self.fn_pressed:
                self.simulate_alt_press = True

    # noinspection PyMethodMayBeStatic
    def fnkey_str(self, event: QKeyEvent, alt_pressed: bool) \
        -> str | None:
        """
        Returns a string ('F1', 'F2', ...) for the pressed fn key.

        Args:
            event
            alt_pressed
        """
        # F-Taste ermitteln
        switcher = {
            QtCore.Qt.Key.Key_F1: 'F1',
            QtCore.Qt.Key.Key_F2: 'F2',
            QtCore.Qt.Key.Key_F3: 'F3',
            QtCore.Qt.Key.Key_F4: 'F4',
            QtCore.Qt.Key.Key_F5: 'F5',
            QtCore.Qt.Key.Key_F6: 'F6',
            QtCore.Qt.Key.Key_F7: 'F7',
            QtCore.Qt.Key.Key_F8: 'F8',
            QtCore.Qt.Key.Key_F9: 'F9',
            QtCore.Qt.Key.Key_F10: 'F10',
            QtCore.Qt.Key.Key_F11: 'F11',
            QtCore.Qt.Key.Key_F12: 'F12',
        }
        fnkey = switcher.get(event.key(), lambda: 'Key not defined.')

        # Return None if the pressed key is not a fn key
        if event.key() not in switcher.keys():
            return None

        # Add "ALT+" to string if ALT/Option key is held down
        if alt_pressed:
            fnkey = 'ALT+' + fnkey  # type: ignore

        return fnkey  # type: ignore

    def create_widget_row(self, fnkeys_list: list[FnKeyDefinition]) -> None:
        """
        Creates a row of widgets (buttons, switches and dropdowns) based on
        the given dictionary.

        Args:
            fnkeys_list
        """
        # Create frame with horizontal layout
        # row_frame = QFrame(self.parent_frame)
        row_frame = QFrame(self)
        row_frame.setFrameShape(QFrame.Shape.StyledPanel)
        row_frame.setAccessibleName('F1F12_Row_Frame')
        row_frame.setObjectName('F1F12_Row_Frame')

        hbox = QHBoxLayout(row_frame)
        hbox.setSpacing(4)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.addWidget(row_frame)

        # Loop fnkey dictionary
        for fnkey in fnkeys_list:
            # Which type of widget to create?
            match fnkey.widget_type:
                case FnKeyType.toggle:
                    widget = self.create_toggle(
                        fnkey.get_key_combo(), fnkey.caption, fnkey.action,
                        fnkey.is_on
                    )
                    widget_frame = widget
                case FnKeyType.dropdown:
                    widget_frame, widget = self.create_combobox(
                        fnkey.get_key_combo(), fnkey.caption,
                        list(fnkey.items.values()),
                        # fnkey.items[fnkey.current_item_index]
                        fnkey.current_item_index
                    )

                    # Connect signal and slot
                    widget.currentIndexChanged.connect(fnkey.action)

                    # widget = widget_frame
                case _:  # FnKeyType.button
                    widget = self.create_button(
                        fnkey.get_key_combo(), fnkey.caption, fnkey.action
                    )
                    widget_frame = widget

            # Set tooltip
            widget.setToolTip(fnkey.tooltip)

            # Add widget to layout
            hbox.addWidget(widget_frame)

            # Save widget instance and slot in dictionary
            self.fnkey_definitions_by_key.update({fnkey.get_key_combo(): fnkey})
            self.widgets.update({fnkey.get_key_combo(): widget})
            self.slots.update({fnkey.get_key_combo(): fnkey.action})

    def create_button(self, fnr, func_text, slot) -> QPushButton:
        """
        Creates a QPushButton, sets the caption to "{fnr}={funktext}" and
        connects the clicked signal with the slot.

        Args:
            fnr
            func_text
            slot

        Returns:
            Instance of the button.
        """
        button: QPushButton = QPushButton(self.parent_frame)
        button.setText(f'{fnr}{self.func_text_separator}{func_text}')
        button.clicked.connect(slot)

        return button

    def create_toggle(self, fnr, func_text, slot, checked) -> QPushButton:
        """
        Creates a QPushButton with switch function, sets the caption to
        "{fnr}={funktext}" and connects the clicked signal with the slot.

        Args:
            fnr
            func_text
            slot
            checked

        Returns:
            Instance of the button (with toggle function).
        """
        button = QPushButton(self.parent_frame)
        button.setText(f'{fnr}{self.func_text_separator}{func_text}')
        button.setCheckable(True)
        button.setChecked(checked)
        button.clicked.connect(slot)

        return button

    def create_combobox(self, fnr, func_text, entries, selected_value) \
            -> tuple[QPushButton, QComboBox]:
        """
        Creates a QPushButton which functions as a frame and  contains a label
        with the function text and a ComboBox with the given entries. The use
        a QPushButton instead of a QFrame ensures that all widgets of the
        fn bar look the same.

        Args:
            fnr
            func_text
            entries
            selected_value

        Returns:
            Instance of the combo box and the frame it is in.
        """
        # Create an empty button to be used as a frame
        frame = QPushButton(self.parent_frame)
        frame.setAccessibleName('Frame_F1F12_ComboBox')
        frame.setObjectName('Frame_F1F12_ComboBox')

        # Create layout for the frame
        frame_layout = QHBoxLayout(frame) if self.compact_mode \
                                          else QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Create label and add to frame
        label = QLabel(frame)
        label.setText(f'{fnr}  {func_text}')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(label)

        # Create combobox and add to frame
        combobox = QComboBox(frame)
        combobox.addItems(entries)
        combobox.setAccessibleName('Frame_F1F12_ComboBox')
        combobox.setObjectName('Frame_F1F12_ComboBox')
        combobox.setCurrentText(selected_value)
        frame_layout.addWidget(combobox)

        # Show popup, when background button is clicked
        frame.clicked.connect(combobox.showPopup)

        # ComboBox: align selected entry centered
        combobox.setEditable(True)
        combobox.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        combobox.lineEdit().setReadOnly(True)

        # ComboBox: align entries within the popup centered
        for i in range(combobox.count()):
            combobox.setItemData(i, Qt.AlignmentFlag.AlignCenter,
                                 Qt.ItemDataRole.TextAlignmentRole)

        return frame, combobox
