"""
pylightlib.qt.StyleSheet
========================

Utility class for processing .css files with variable support and
light/dark mode handling.

This module provides the `StyleSheet` class with a static method
`replace_variables()` that parses CSS files containing custom variables
and replaces them based on the current color scheme (light or dark mode)
detected via the given `QApplication`.

The expected .css structure:

    [variable definitions]
    #-----#
    [CSS content]

Variable syntax:

    var_name = light_value/dark_value

    or, for shared values:

    var_name = value

Usage example in CSS:

    background-color: {bg_color};

The method strips everything before "#-----#" and replaces all placeholders
with their corresponding values, depending on the current theme.

"""

# == Qt imports (use external folder when app is bundled for LGPL conformity) ==
from pylightlib.msc.SysPathHandler import SysPathHandler

SysPathHandler().set_new_sys_path()
try:
    # import PySide6
    from PySide6 import QtCore                            # type: ignore # noqa
    from PySide6 import QtGui                             # type: ignore # noqa
    from PySide6.QtGui import QPalette, QImage, QPainter  # type: ignore # noqa
    from PySide6.QtWidgets import QPushButton, QStyleOptionButton, QApplication  # type: ignore # noqa
except ImportError as e:
    print(f'Import Error ({__file__}):\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()


class StyleSheet:
    """
    This class provides methods to process .css files with variables.

    Methods
    -------
    replace_variables(text, qapp)
        Processes the content of a .css file with variables and replaces them
        based on the current color scheme.
    """
    @staticmethod
    def replace_variables(text: str, qapp: QApplication) -> str:
        """
        Processes the content of a .css file with variables.

        The file must have the following structure:

            ```
            [variable definitions]
            #-----#
            [CSS code]
            ```

        The syntax of the variable definitions is:

            ```
            var_name = value_light_mode/value_light_mode
            ```

        Or:

            ```
            var_name = value
            ```
            (same value for light and dark mode)

        For example:

            ```
            bg_color = #002c4e/#ffffff
            ```

        To use a variable it has to be enclosed by curly brackets.
        For example:

            ```
            background-color: {bg_color};
            ```

        The variables/placeholders will be replaced with the values. Everything
        before "#-----#" is removed from the given string.

        Parameters
        ----------
        text : str
            The content of the .css file.
        qapp : QApplication
            QApplication object.

        Returns
        -------
        str
            The processed CSS code.
        """
        # Check if dark mode is activated
        color_scheme = qapp.styleHints().colorScheme()

        # if color_scheme == PySide6.QtCore.Qt.ColorScheme.Light:
        if color_scheme == QtCore.Qt.ColorScheme.Light:
            dark_mode = False
        else:
            dark_mode = True

        # Get variable definitions and css code
        variable_definitions, style_sheet = text.split('#-----#')[0], \
            text.split('#-----#')[1]

        # Split variable definitions into lines
        vars_lines = variable_definitions.splitlines()

        # Loop all variables and replace the placeholders with the values
        for i in range(0, len(vars_lines)):
            if len(vars_lines[i].split('=')) == 2:
                # Get variable name
                variable_name = vars_lines[i].split('=')[0].replace(' ', '')

                # Get values for light and dark mode
                values = vars_lines[i].split('=')[1].replace(' ', '')
                values_list = values.split('/')

                if dark_mode and len(values_list) == 2:
                    value = values_list[1]
                else:
                    value = values_list[0]

                # Replace variable name with value
                style_sheet = style_sheet.replace('{' + variable_name + '}',
                                                  value)

        return style_sheet
