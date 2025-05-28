"""
pylightlib.txtl.CustomBindings
==============================

Module for managing custom key bindings in Textual applications using
YAML configuration.


Author:
    Corvin Gröning

Date:
    2025-05-24

Version:
    0.1

This module defines a class for managing custom keyboard bindings in
a [Textual](https://github.com/Textualize/textual) application.
The `CustomBindings` class loads key binding definitions from a YAML file,
organizes them by logical groups (e.g., `_global`, `editor`, `viewer`)
and exposes them as Textual `Binding` objects.

Each binding definition in the YAML file includes attributes such as `key`,
`action`, `description` and optional metadata like `tooltip`, `priority`, `id`,
`show`, and `system`. The class processes this information to support
context-sensitive key mappings, display hints, and advanced input behavior.

The module also supports automatic generation of copy/paste bindings and
offers helper methods to determine if actions should be visible or active based
on the current application context.

Intended for use in modular or tabbed interfaces, this system helps keep key
binding logic centralized and configurable without hard-coding values into
application logic.
"""
import re
import yaml

from textual.app import App
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Input, TextArea


class CustomBindings():
    """
    Singleton class to manage custom key bindings loaded from a YAML file for
    use in a Textual application.

    The YAML file is structured as a dictionary of key binding groups. Each key
    in the dictionary represents a group (e.g., "_global", "counter",
    "another"), and its value is a list of key binding definitions. Each binding
    is described by fields like `key`, `action`, `description`, `tooltip`
    and optional attributes such as `show`, `priority`, `id` and `system`.

    The class reads this YAML file and converts each binding entry into
    a `Binding` instance from the Textual framework. These instances are stored
    in the `bindings_dict`, grouped by their group name.

    The `get_bindings()` method returns all bindings as a single list, sorted
    by key (e.g., f1, f2, ..., f12), and is typically used to populate
    the `BINDINGS` property of a Textual app.

    The `action_to_groups` dictionary maps each action names to the group(s) it
    belongs to. This enables logic to determine which group a given action is
    part of.

    The `global_actions` list contains all actions from the "_global" group.
    These are meant to be always shown, regardless of the currently active tab
    or view.

    The `action_to_groups` and `global_actions` structures are intended to be
    used within the `check_action()` method to determine whether a key binding
    should be displayed, depending on the currently selected tab or context in
    the app.

    Attributes:
        YAML_FILE: Path to the YAML file containing key bindings.
        bindings_dict_raw: Raw data loaded from the YAML file.
        bindings_dict: Processed key bindings grouped by their group name.
        action_to_groups: Maps actions to the groups they belong to.
        global_actions: List of actions that are always shown globally.
    """
    YAML_FILE = 'data/bindings.yaml'
    bindings_dict_raw: dict[str, list[dict[str, str]]]
    bindings_dict: dict[str, list[Binding]] = {}
    action_to_groups: dict[str, list[str]] = {}
    global_actions: list[str] = []


    def __init__(self, with_copy_paste_keys: bool = False):
        """
        Reads the YAML file and processes the bindings into a structured format.

        Args:
            app: The Textual application instance that uses these bindings.
        """
        self.read_yaml_file()
        self.process_bindings()
        self.process_global_always_bindings()

        if with_copy_paste_keys:
            self.add_copy_paste_bindings()

    def read_yaml_file(self):
        """
        Loads the binding definitions from the YAML file into a dictionary.
        """
        with open(self.YAML_FILE, 'r', encoding='utf-8') as file:
            self.bindings_dict_raw = yaml.safe_load(file)

    def process_bindings(self):
        """
        Processes the raw data from the YAML file into a structured format
        suitable for use in the Textual application. It converts each binding
        into a `Binding` instance and organizes them by their group name.
        Also builds the `action_to_groups` mapping and stores the name of
        global actions in `global_actions`.
        """
        # Loop groups
        for group, bindings in self.bindings_dict_raw.items():
            if group not in self.bindings_dict:
                self.bindings_dict[group] = []

            # Loop bindings
            for binding in bindings:
                key         = self.parse_key(binding.get('key'))
                action      = self.parse_action(binding.get('action'), group)
                description = self.parse_description(binding.get('description'))
                show        = self.parse_show(binding.get('show'))
                key_display = self.parse_key_display(
                                  key, binding.get('key_display'), group
                              )
                priority    = self.parse_priority(binding.get('priority'))
                tooltip     = self.parse_tooltip(binding.get('tooltip'))
                id          = self.parse_id(binding.get('id'))
                system      = self.parse_system(binding.get('system'))

                # Skip if any required field is missing
                if key is None or action is None or description is None:
                    continue

                binding_instance = Binding(
                    key        =key,
                    action     =action,
                    description=description,
                    show       =show,
                    key_display=key_display,
                    priority   =priority,
                    tooltip    =tooltip,
                    id         =id,
                    system     =system
                )
                self.bindings_dict[group].append(binding_instance)

                # Add action to action_to_groups mapping
                if action not in self.action_to_groups:
                    self.action_to_groups[action] = [group]
                else:
                    self.action_to_groups[action].append(group)

                # Add action to global actions if applicable
                if group == '_global':
                    self.global_actions.append(action)

    def process_global_always_bindings(self):
        """
        Processes the bindings from the '_global_always' group and adds them
        to the `action_to_groups` mapping. This ensures that these bindings
        are always valid and can be used across all groups.
        """
        for binding in self.bindings_dict['_global_always']:
            for group in self.bindings_dict.keys():
                if group in ['_global', '_global_always']:
                    continue

                if binding.action not in self.action_to_groups:
                    self.action_to_groups[binding.action] = []

                self.action_to_groups[binding.action].append(group)

    def add_copy_paste_bindings(self):
        """
        Adds copy and paste key bindings to the global group.
        """
        # Define bindings
        copy_val_binding = Binding(
            key='f1',
            action='global_copy_widget_value_to_clipboard',
            description='CpyVal',
            key_display='*F1',
            tooltip='Copy widget value to clipboard',
        )
        copy_sel_binding = Binding(
            key='f2',
            action='global_copy_selection_to_clipboard',
            description='CpySel',
            key_display='*F2',
            tooltip='Copy selected text to clipboard',
        )
        paste_binding = Binding(
            key='f3',
            action='global_paste_from_clipboard',
            description='Paste',
            key_display='*F3',
            tooltip='Paste text from clipboard',
        )
        replace_binding = Binding(
            key='f4',
            action='global_replace_widget_value_from_clipboard',
            description='Replace',
            key_display='*F4',
            tooltip='Replace the widget value with the text from the clipboard',
        )
        copy_paste_bindings = [copy_val_binding, copy_sel_binding,
                               paste_binding, replace_binding]

        # Add copy and paste bindings to the global group
        if '_global' not in self.bindings_dict:
            self.bindings_dict['_global'] = []
        self.bindings_dict['_global'].extend(copy_paste_bindings)

        # Update action_to_groups and global_actions
        for binding in copy_paste_bindings:
            if binding.action not in self.action_to_groups:
                self.action_to_groups[binding.action] = ['_global']
            self.global_actions.append(binding.action)

    def get_bindings(self):
        """
        Returns a list (sorted by the key) of all bindings across all groups.

        Returns:
            A list of `Binding` instances sorted by their key.
        """
        def sort_key(binding: Binding):
            # Transform a key like "f1" to "f01" for sorting
            match = re.match(r"(f)(\d+)", binding.key.lower())
            if match:
                return f"{match.group(1)}{int(match.group(2)):02d}"
            return binding.key.lower()

        # Sort each group of bindings by their key
        for group, bindings in self.bindings_dict.items():
            self.bindings_dict[group] = sorted(bindings, key=lambda b: b.key)

        # Combine all bindings into a single list and sort by key
        bindings_list: list[Binding] = []
        for bindings in self.bindings_dict.values():
            bindings_list.extend(bindings)
        bindings_list = sorted(bindings_list, key=sort_key)

        return bindings_list

    def handle_copy_widget_value_to_clipboard(self, app) -> None:
        """
        Copies value of the currently focused input widget to the clipboard.

        Args:
            app: The Textual application instance.
        """
        focused_widget = app.focused

        if hasattr(focused_widget, 'value'):
            app.copy_to_clipboard(focused_widget.value)
        elif hasattr(focused_widget, 'text'):
            app.copy_to_clipboard(focused_widget.text)
        else:
            return

        app.notify('Value copied to clipboard!')

    def handle_copy_selection_to_clipboard_action(self, app: App):
        """
        Copies the selected text from the currently focused input widget to
        the clipboard.

        Args:
            app: The Textual application instance.
        """
        focused_widget: Widget | None = app.focused

        if hasattr(focused_widget, 'selected_text'):
            app.copy_to_clipboard(focused_widget.selected_text)  # type: ignore

        app.notify('Selection copied to clipboard!')

    def handle_paste_from_clipboard(self, app: App, replace: bool = False) \
    -> None:
        """
        Pastes the text from the clipboard to the currently focused input
        widget at cursor position.

        Args:
            app: The Textual application instance.
            replace: If True, replaces the current value with the
                     clipboard text.
                     If False, inserts the clipboard text at the
                     cursor position.
        """
        # Check if a widget is focused
        focused_widget: Widget | None = app.focused

        if not focused_widget:
            app.notify('No widget focused.', severity='warning')
            return

        # Check if clipboard is empty
        clipboard_text = app.clipboard
        if not clipboard_text:
            app.notify('Clipboard is empty.', severity='warning')
            return

        # Paste into Input/TextArea
        if isinstance(focused_widget, Input):
            self.paste_into_input(app, focused_widget, clipboard_text, replace)
        elif isinstance(focused_widget, TextArea):
            self.paste_into_textarea(app, focused_widget, clipboard_text,
                                      replace)
        else:
            app.notify('Focused widget does not support pasting text.', severity='warning')

    def paste_into_input(self, app, input: Input, text: str, replace: bool) \
    -> None:
        """
        Pastes the given text into the input widget at the cursor position.

        Args:
            app: The Textual application instance.
            input: The Input widget where the text will be pasted.
            text: The text to paste.
            replace: If True, replaces the current value with the text.
                     If False, inserts the text at the cursor position.
        """
        if replace:
            input.value = text
        else:
            cursor_pos = input.cursor_position or 0
            input.insert(text, cursor_pos)
            input.cursor_position = cursor_pos + len(text)

        app.notify('Text pasted into input field!')

    def paste_into_textarea(self, app, textarea: TextArea, text: str,
                            replace: bool) -> None:
        """
        Pastes the given text into the textarea at the cursor position.

        Args:
            app: The Textual application instance.
            textarea: The TextArea widget where the text will be pasted.
            text: The text to paste.
            replace: If True, replaces the current value with the text.
                     If False, inserts the text at the cursor position.
        """
        if replace:
            textarea.text = text
        else:
            cursor_pos: tuple[int, int] = textarea.cursor_location or (0, 0)
            textarea.insert(text, cursor_pos)
            textarea.cursor_location = (cursor_pos[0], cursor_pos[1]+len(text))

        app.notify('Text pasted into text area!')

    def handle_check_action(self, action: str, parameters: tuple[object, ...],
                            active_group: str, show_global_keys: bool = False) \
    -> bool | None:
        """
        Checks if a given action should be displayed based on the current
        active group and whether to show global keys.

        This is meant to be used in the check_action method of a Textual app.

        Args:
            action: The action to check.
            parameters: Parameters for the action (not used).
            active_group: The currently active group or tab.
            show_global_keys: Whether to show only global keys.

        Returns:
            True if the action should be displayed, False otherwise.
        """
        # Show only global keys?
        if show_global_keys:
            if self.is_global_key(action):
                return True
            else:
                return False

        # Ignore actions that are not defined in custom bindings
        if not self.is_custom_action(action, active_group):
            return True

        # If the action is not global, check if it belongs to the current tab
        if active_group in self.action_to_groups[action]:
            return True

        return False

    def is_global_key(self, action: str) -> bool:
        """
        Checks if the given action belongs to a global key binding.

        Args:
            action: The action to check.

        Returns:
            True if the action is global, False otherwise.
        """
        return action in self.global_actions

    def is_custom_action(self, action: str, group: str) -> bool:
        """
        Checks if the given action is a custom action defined in the bindings.

        Args:
            action: The action to check.
            group: The group to check against.

        Returns:
            True if the action is a custom action, False otherwise.
        """
        return action in self.action_to_groups

    def action_belongs_to_group(self, action: str, group: str) -> bool:
        """
        Checks if the given action belongs to the specified group.

        Args:
            action: The action to check.
            group: The group to check against.

        Returns:
            True if the action belongs to the group, False otherwise.
        """
        return group in self.action_to_groups.get(action, [])

    def parse_key(self, key: str | None) -> str | None:
        return key

    def parse_action(self, action: str | None, group: str) -> str | None:
        if action is None or group is None:
            return None
        else:
            return f'{group.replace('_', '')}_{action}'

    def parse_description(self, description: str | None) -> str | None:
        return description

    def parse_show(self, show: str | None) -> bool:
        if show is None:
            return True
        else:
            return bool(show)

    def parse_key_display(self, key: str | None, key_display: str | None,
                          group: str) -> str | None:
        if key is None:
            return None

        match = re.fullmatch(r"(f)(\d+)", key.lower())
        if match:
            key_display = f'F{int(match.group(2))}'

        if group == '_global':
            key_display = f'*{key_display}'

        return key_display

    def parse_priority(self, priority: str | None) -> bool:
        if priority is None:
            return False
        else:
            return bool(priority)

    def parse_tooltip(self, tooltip: str | None) -> str:
        if tooltip is None:
            return ''
        else:
            return tooltip

    def parse_id(self, id: str | None) -> str | None:
        if id is None:
            return None
        else:
            return id

    def parse_system(self, system: str | None) -> bool:
        if system is None:
            return False
        else:
            return bool(system)