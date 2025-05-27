"""
pylightlib.txtl.CustomDataTable
===============================

Extension of Textual's DataTable with support for flexible column resizing.

Author:
    Corvin Gröning

Date:
    2025-05-24

Version:
    0.1

This module defines `CustomDataTable`, a subclass of Textual's `DataTable`
with additional capabilities for handling dynamic resizing of table columns
based on available space.

The primary enhancement is the introduction of *flexible columns* — a list of
column keys that automatically adjust their widths when the table is resized.
This allows developers to create responsive and adaptive data tables where
certain columns expand or contract depending on the widget size, while others
remain fixed.

The class overrides the `on_resize` method to calculate the total available
width and distribute it proportionally among the flexible columns. It also
provides helper methods for determining fixed column widths and adjusting
layout accordingly.

This is particularly useful for applications with tabular data in dynamic
layouts or where users resize windows and expect columns to adapt gracefully.

"""

from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable
from textual.widgets._data_table import ColumnKey, Column


class CustomDataTable(DataTable):
    """
    CustomDataTable is a subclass of DataTable that provides additional
    functionality for handling flexible column widths and resizing.

    Attributes:
        flexible_columns: List of column keys that should be flexible in width
            (will be adjusted according to window width).
    """
    flexible_columns: list[ColumnKey] = []


    class Mounted(Message):
        def __init__(self, sender: Widget):
            super().__init__()
            self.sender = sender


    def __init__(self, **kwargs):
        """
        Initializes the DataTable.
        """
        super().__init__(**kwargs)


    def on_mount(self) -> None:
        """
        Handles the mount event of the DataTable.

        This method is called when the DataTable is mounted in the application.
        It posts a Mounted message to notify that the DataTable is ready.
        This is useful for initializing any additional functionality that
        depends on the DataTable being fully mounted.

        Example:
            ```
            @on(CustomDataTable.Mounted)
            async def on_table_mounted(self, event: CustomDataTable.Mounted) \
            -> None:
                # Add columns and rows to the table
                pass
            ```
        """
        self.post_message(self.Mounted(self))

    def on_resize(self) -> None:
        """
        Handles the resize event of the DataTable.

        Adjusts the widths of the flexible columns based on the new size of
        the table.
        """
        table_width = self.size.width - len(self.columns) * 2
        fixed_widths = self.get_fixed_column_widths()
        self.adjust_flexible_columns(table_width, fixed_widths)
        self.refresh()

    def get_fixed_column_widths(self) -> int:
        """
        Returns the total width of all fixed-width columns in the table.

        This is used to calculate the available width for flexible columns.

        Returns:
            The total width of all fixed-width columns.
        """
        fixed_widths = 0

        for column_key in self.columns:
            column: Column = self.columns[column_key]

            if column_key not in self.flexible_columns:
                fixed_widths += column.width

        return fixed_widths

    def adjust_flexible_columns(self, table_width: int, fixed_width: int) \
    -> None:
        """
        Adjusts the widths of the flexible columns based on the available
        width in the table.

        Args:
            table_width: The total width of the table.
            fixed_width: The total width of all fixed-width columns.
        """
        for column_key in self.columns:
            column: Column = self.columns[column_key]

            if column_key in self.flexible_columns:
                column.auto_width = False
                column.width = int(
                    (table_width - fixed_width) / len(self.flexible_columns)
                )

    # def get_current_id(self) -> int:
    #     """
    #     Returns the ID of the currently selected topic.

    #     Returns:
    #         int: The ID of the currently selected topic.
    #     """
    #     selected_row = self.get_row_at(self.cursor_row)
    #     return int(selected_row[0].plain.strip())

    # def delete_selected_row(self) -> None:
    #     """
    #     Deletes the currently selected row from the table.
    #     """
    #     if self.cursor_row is not None:
    #         row_key, _ = self.coordinate_to_cell_key(self.cursor_coordinate)
    #         self.remove_row(row_key)