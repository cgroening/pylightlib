"""
pylightlib.qt.TableHelper
=========================

Utility class to populate and manage QTableWidget with structured data.

This module provides the `TableHelper` class which simplifies populating
and configuring a `QTableWidget` using structured data for headers and
rows.

Header structure:
    head = [[column_name, width, alignment, readonly, data_key], ...]

Data structure:
    data = [{key1: value1, key2: value2, ...}, ...]

Features:

- Automatically sets up column headers with fixed or stretch width
- Supports column alignment (left, center, right)
- Handles read-only columns
- Adds, sets, and sorts data rows dynamically

Useful for form-based or tabular Qt applications that need clean and
configurable table views.

"""

# Libs

# == Qt imports (use external folder when app is bundled for LGPL conformity) ==
from pylightlib.msc.SysPathHandler import SysPathHandler

SysPathHandler().set_new_sys_path()
try:
    from PySide6.QtCore import Qt  # type: ignore # noqa
    from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView  # type: ignore # noqa
except ImportError as e:
    print(f'Import Error ({__file__}):\n    ' + str(e.msg))
    exit()
SysPathHandler().restore_sys_path()


class TableHelper:
    """
    This class helps to create a table with QTableWidget.

    It receives a QTableWidget instance, a two-dimensional list for the table head and a
    two-dimensional list for the table data.

    Structure of the list for the table head:
    head = [[column_name: str, width: int, justification: str, readonly: bool,
             column_no_in_data_list: int],  # Column 1
            ...
           ]

    Structure of the list for the table data:
    data = [[value_1, value_2, ...],  # Row 1
               ...
              ]

    The QTableWidget will be filled with data from these two lists.

    Attributes
    ----------
    tbl : QTableWidget
        Instance of the QTableWidget.
    head : list[tuple[str, int, str, bool, str]]
        Two-dimensional list with a list for each column.
    data : list[dict[str, str]]
        Two-dimensional list with a list for each row.
    """
    tbl: QTableWidget
    head: list[tuple[str, int, str, bool, str]]
    data: list[dict[str, str]]


    def __init__(self, table_widget: QTableWidget,
                 table_head: list[tuple[str, int, str, bool, str]],
                 table_data: list[dict[str, str]]):
        """
        Receives the instance of the QTableWidget and the lists for table head and table data.

        Parameters
        ----------
        table_widget : QTableWidget
            Instance of the QTableWidget.
        table_head : list[tuple[str, int, str, bool, str]]
            Two-dimensional list with a list for each column.
        table_data : list[dict[str, str]]
            Two-dimensional list with a list for each row.
        """
        # Save parameters in class variables
        self.tbl = table_widget
        self.head = table_head
        self.data = table_data

        # Create table
        self.create_head()
        # self.sort_data_list()
        self.add_data()

    def create_head(self) -> None:
        """
        Creates the table head and sets the width for each column.
        """
        # Set number of columns
        self.tbl.setColumnCount(len(self.head))

        # Set the heading for each column
        header_lbls = []
        for i in range(len(self.head)):
            header_lbls.append(self.head[i][0])
        self.tbl.setHorizontalHeaderLabels(header_lbls)

        # Set column widths
        width: int
        for i in range(len(self.head)):
            width = self.head[i][1]
            header = self.tbl.horizontalHeader()

            if width > 0:
                self.tbl.setColumnWidth(i, width)
                header.resizeSection(i, width)
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.tbl.horizontalHeader().setStretchLastSection(False)

    def sort_data_list(self) -> None:
        """
        Sorts the columns of the data list according to the table head.
        """
        # List for the sorted data
        data_sorted = []

        # Loop table rows
        for row_no in range(len(self.data)):
            # List for the cells of the row
            row_sorted = []

            # Loop cells of the row
            for cell in range(len(self.head)):

                # Get column number and value of the cell
                column_no_in_data_list = self.head[cell][4]
                cell_value = self.data[row_no][column_no_in_data_list]

                # Add cell value to list for the row
                if int(column_no_in_data_list) >= 0 and cell_value is not None:
                    row_sorted.append(self.data[row_no][column_no_in_data_list])
                else:
                    row_sorted.append('')

            # Add row to sorted data list
            data_sorted.append(row_sorted)

        # Replace old data list with sorted list
        self.data = data_sorted  # type: ignore

    def add_data(self) -> None:
        """
        Adds the data from the dictionary data to the table.
        """
        data = self.data

        # Set the number of rows
        self.tbl.setRowCount(len(data))

        # Loop rows of data list
        for row in range(len(data)):
            # Loop columns
            for column in range(len(self.head)):
                # Cell value
                column_name = self.head[column][4]

                if column_name in data[row]:
                    value = str(data[row][column_name])
                else:
                    value = ''

                # Justification (left, right oder center)
                if self.head[column][2] == 'right':
                    justification = Qt.AlignRight
                elif self.head[column][2] == 'center':
                    justification = Qt.AlignCenter
                else:
                    justification = Qt.AlignLeft

                # Read-only
                readonly = self.head[column][3]

                # Create QTableWidgetItem and add to QTableWidget
                item = QTableWidgetItem(value)
                item.setTextAlignment(justification | Qt.AlignVCenter)
                if readonly:
                    # item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    # item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
                self.tbl.setItem(row, column, item)

    def add_data_list(self) -> None:
        """
        Adds the sorted data to the table.
        """
        data = self.data

        # Set the number of rows
        self.tbl.setRowCount(len(data))

        # Loop rows of data list
        for row in range(len(data)):
            # Loop cells of the row
            for cell in range(len(data[0])):
                # Cell value
                value = str(data[row][int(cell)])  # type: ignore

                # Justification (left, right oder center)
                if self.head[cell][2] == 'right':
                    justification = Qt.AlignRight
                elif self.head[cell][2] == 'center':
                    justification = Qt.AlignCenter
                else:
                    justification = Qt.AlignLeft

                # Read-only
                readonly = self.head[cell][3]

                # Create QTableWidgetItem and add to QTableWidget
                item = QTableWidgetItem(value)
                item.setTextAlignment(justification)
                if readonly:
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tbl.setItem(row, cell, item)

                Qt.AlignmentFlag.AlignLeft

    def add_row(self, index: int) -> None:
        """
        Adds a new row to the table.

        Parameters
        ----------
        index : int
            Index of the new row.
        """
        # Insert row
        self.tbl.insertRow(index)

        # Set justification and read-only
        justification: int

        for column in range(len(self.head)):
            read_only: bool = False

            match self.head[column][2]:
                case 'right':
                    justification = Qt.AlignRight
                case 'center':
                    justification = Qt.AlignCenter
                case _:
                    justification = Qt.AlignLeft

            if self.head[column][3]:
                read_only = True

            item = QTableWidgetItem()
            item.setTextAlignment(justification)
            if read_only:
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.tbl.setItem(index, column, item)

    def set_cell_value(self, row: int, column: int, value: str) -> None:
        """
        Sets the value of a cell.

        Parameters
        ----------
        row : int
            Row of the cell.
        column : int
            Column of the cell.
        value : str
            Value to set.
        """
        # Get justification and read-only
        justification: int
        read_only: bool = False

        match self.head[column][2]:
            case 'right':
                justification = Qt.AlignRight
            case 'center':
                justification = Qt.AlignCenter
            case _:
                justification = Qt.AlignLeft

        if self.head[column][3]:
            read_only = True

        item = QTableWidgetItem(value)
        item.setTextAlignment(justification)
        if read_only:
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.tbl.setItem(row, column, item)
