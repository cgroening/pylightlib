"""
pylightlib.tk.table
===================

A fully scrollable, editable and styleable table widget for Tkinter GUIs.

Author:
    Corvin Gröning

Date:
    2025-03-22

Version:
    0.1

This module implements the `Table` class — a high-level widget for displaying
and editing tabular data in Tkinter using multiple synchronized
`EditableListbox` instances as columns.

The table supports the following features:

- Editable cells (with optional read-only columns)
- Fully synchronized vertical scrolling and selection across columns
- Column resizing via mouse drag on column headers
- Row, column, and cell highlighting using a customizable color scheme
- Arrow key navigation (left/right), PageUp/PageDown support
- Platform-aware mouse wheel behavior
- Responsive sizing and highlight extension framing for selected rows
- Automatic model update on cell edit

Internally, the `Table` widget uses `ScrollFrame`, `FramedWidget` and
`EditableListbox` components from the PyLightFramework for flexibility and
visual consistency. It is particularly suited for applications requiring rich
data interaction in tabular format.

To define a table, the user must provide:

- a list of `TableColumn` definitions (with heading, width, justification, etc.)
- a 2D list of data
- a `DefaultColorScheme` instance for consistent styling

"""

# Libs
import tkinter
import tkinter as tk
import tkinter.font as tkfont
from dataclasses import dataclass

# PyLightFramework
from pylightlib.tk.EditableListbox import EditableListbox
from pylightlib.tk.ScrollFrame import ScrollFrame
from pylightlib.tk.FramedWidget import FramedWidget
from pylightlib.tk.DefaultColorScheme import DefaultColorScheme

# import win32com.client


@dataclass
class TableColumn:
    """
    Describes a single column in a table.

    Attributes:
        heading:   Column heading.
        width:     Column width (if 0 width will be set automatically).
        justify:   Justification of the content ('left', 'center' or 'right').
        read_only: Indicates if the values of the column can be edited.
    """
    heading: str
    width: int = 0
    justify: str = 'left'
    read_only: bool = False


class Table:
    """
    Creates a fully functional table widget using one Listbox per column.
    All listboxes are synchronized in scrolling, selection, and highlighting.

    Features:

    - Editable cells (unless marked as read-only)
    - Scrollable columns and rows
    - Customizable color scheme and font
    - Column headers with resizable widths
    - Arrow key and page navigation
    - Highlighting of selected rows, columns, and cells

    Designed for use with the PyLightFramework.

    Attributes:
        master:         Master frame for this widget.
        head:           List of the column headings in left-to-right order.
        data:           Multidimensional list of the table data (rows, columns).
        color_scheme:   Instance of the color scheme of the app.
        font:           Font family and size.
        padding_frames: List of the padding frames around listboxes.
        lbls: List of the instances of the labels for the column headings.
        lbox: List of the listboxes for each column.
        highlight_ext_frames_left:  List of the frames to extend the highlight
                                    for active row (left).
        highlight_ext_frames_right: List of the frames to extend the highlight
                                    for active row (right).
        outer_frame:   Outer frame which contains the inner frame and the
                       vertical scrollbar.
        inner_frame:   Inner frame which contains the listboxes and the
                       horizontal scrollbar.
        row_height:    Height of a row (= height of a listbox item) in pixels.
        visible_rows:  Number of visible rows.
        current_row:   ID of the currently selected row.
        selected_cell: Row and column of the currently selected cell.
        default_bg:    Dictionary for the default background colors.
        selected_bg:   Dictionary for the background colors of selected item,
                       column and row.
        default_fg:    Dictionary for the default foreground colors.
        selected_fg:   Dictionary for the foreground colors of selected item,
                       column and row.
        os: Name of the operating system.

    """
    master: tk.Frame
    head: list[TableColumn] = []
    data: list[list[str]] = [[]]
    color_scheme: DefaultColorScheme
    font: dict[str, str | int] = {'family': 'Monaco', 'size': 14}
    padding_frames: list[tk.Frame] = []
    lbls: list[FramedWidget] = []
    lbox: list[EditableListbox] = []
    highlight_ext_frames_left: list[tk.Frame] = []
    highlight_ext_frames_right: list[tk.Frame] = []
    outer_frame: tk.Frame
    inner_frame: ScrollFrame
    row_height: float = 20.0
    visible_rows: int = 0
    current_row: int = 0
    selected_cell: dict[str, int] = {'row': 0, 'col': 0}
    default_bg: dict
    selected_bg: dict
    default_fg: dict
    selected_fg: dict
    os: str = 'mac'


    def __init__(self, master: tk.Frame, head: list[TableColumn],
                 data: list[list[str]], color_scheme: DefaultColorScheme):
        """
        Create a table widget with the given data.

        Args:
            master: Master frame for this widget.
            head:   List of the column headings in left-to-right order.
            data:   Multidimensional list of the table data (rows, columns).
            color_scheme: Instance of the color scheme of the app.
        """
        self.master = master
        self.head = head
        self.data = data
        self.color_scheme = color_scheme

        # Set colors
        cls = self.color_scheme
        self.default_bg = {
            'border': cls.app['accent4'],
            'column': cls.app['accent1'],
            'column_heading': cls.app['accent2'],
        }
        self.selected_bg = {
            'cell': cls.app['accent4'],
            'column': cls.app['accent2'],
            'column_heading': cls.app['accent4'],
            'row': cls.app['accent2']
        }
        self.default_fg = {
            'cell': cls.app['fg'],
            'column': cls.app['fg'],
            'column_heading': cls.app['fg'],
        }
        self.selected_fg = {
            'cell': cls.app['fg_highlight'],
            'column': cls.app['fg'],
            'column_heading': cls.app['fg_highlight'],
        }

        # Create table and fill with given data
        self.create_frames()
        self.create_head()
        self.create_listboxes()
        self.configure_vertical_scrollbar()
        self.add_data()

    def create_frames(self) -> None:
        """
        Creates two frames:

        - Outer frame which contains the inner frame and vertical scrollbar.
        - Inner frame which contains the listboxes and horizontal scrollbar.

        """
        # Create frames
        self.outer_frame = tk.Frame(master=self.master)
        self.inner_frame = ScrollFrame(master=self.outer_frame,
                                       color_scheme=self.color_scheme)

        # Pack inner frame and configure outer frame
        self.inner_frame.grid(row=0, column=0, sticky='nesw')  # type: ignore
        self.outer_frame.rowconfigure(0, weight=1)
        self.outer_frame.columnconfigure(0, weight=1)

        # Add callback which will be run if the canvas within the inner frame
        # changes size
        self.inner_frame.canvas.bind('<Configure>', self.change_size)

    def create_head(self) -> None:
        """
        Creates a label for each column heading.
        """
        # Loop column headings
        for i in range(len(self.head)):
            # Get column heading
            heading = self.head[i].heading

            # Create label, only add right border if it's the last column
            if i == len(self.head) - 1:
                borderright = 1
            else:
                borderright = 0
            lbl = FramedWidget(master=self.inner_frame, widget='label',
                               text=' ' + heading, anchor='w', relief='flat',
                               borderwidth=1, borderright=borderright,
                               background=self.default_bg['column_heading'])

            lbl.grid(row=0, column=i, sticky='nesw')
            lbl.columnconfigure(i, weight=1)

            # Add label to dictionary
            self.lbls.append(lbl)

            # Callbacks: Cursor over label + Cursor over label with B1 pressed
            # noinspection PyCallingNonCallable
            self.lbls[i].bind('<Motion>', self.label_mouse_motion)  # type: ignore
            # noinspection PyCallingNonCallable
            self.lbls[i].bind('<B1-Motion>', self.label_b1_mouse_motion)  # type: ignore

    def create_listboxes(self) -> None:
        """
        Creates a listbox for each column.
        """
        font = tkfont.Font(family=self.font['family'], size=self.font['size'])  # type: ignore
        padding_x = 5  # TODO: put this somewhere else

        # Create a listbox for each column
        for i in range(len(self.head)):
            # Create a frame which works as a border for the listbox
            # noinspection PyTypeChecker
            border_frame = tk.Frame(master=self.inner_frame,  # type: ignore
                                    background=self.default_bg['border'])
            border_frame.grid(row=1, column=i, sticky=tk.NSEW)

            # Only add right border if it's the last listbox
            if i == len(self.head) - 1:
                border_x = (1, 1)
            else:
                border_x = (1, 0)

            # Create padding frame
            padding_frame = tk.Frame(master=border_frame,
                                     background=self.default_bg['column'])
            padding_frame.pack(fill='both', padx=border_x)
            self.padding_frames.append(padding_frame)

            # Create listbox (exportselection=0 allows a selection in multiple
            # listboxes)
            lbox = EditableListbox(master=padding_frame, exportselection=0,
                                   borderwidth=0, highlightthickness=0,
                                   activestyle='none', font=font)

            # Put listbox in padding frame
            # lbox.grid(row=0, column=0, sticky='nesw', padx=padding_x)
            lbox.pack(fill='both', padx=padding_x)
            border_frame.grid_columnconfigure(0, weight=1)

            # Creates frames for extension of active line highlight
            highlight_ext_left = tk.Frame(master=border_frame,
                                          background=self.default_bg['column'],
                                          width=padding_x, height=10)
            highlight_ext_right = tk.Frame(master=border_frame,
                                           background=self.default_bg['column'],
                                           width=padding_x, height=10)
            self.highlight_ext_frames_left.append(highlight_ext_left)
            self.highlight_ext_frames_right.append(highlight_ext_right)

            # Place extensions frames in padding frame, position and size will
            # be adjusted in selection_changed
            highlight_ext_left.place(x=1, y=5)
            highlight_ext_right.place(x=10, y=5)

            # Set colors
            lbox.configure(bg=self.default_bg['column'],
                           fg=self.color_scheme.app['fg'])

            # Set style for active row
            lbox.configure(activestyle=tkinter.DOTBOX)

            # Set column width, justification and read-only
            # noinspection PyTypeChecker
            lbox.configure( \
                width=self.head[i].width, justify=self.head[i].justify \
            )   # type: ignore
            lbox.read_only = self.head[i].read_only

            # Add listbox to dictionary
            self.lbox.append(lbox)

            '''Callbacks'''
            # Scrolling
            lbox.bind('<<ListboxSelect>>', self.selection_changed)
            lbox.bind('<MouseWheel>', self.mouse_scroll)

            # Supress scrolling of a single listbox: if an item is wider than
            # the listbox and cursor is moved with the left mouse button pressed
            # while over the item, nothing should happen
            lbox.bind('<B1-Leave>', lambda event: 'break')

            # Arrow keys
            lbox.bind('<Left>', self.arrow_left)
            lbox.bind('<Right>', self.arrow_right)

            # Item was edited
            lbox.bind('<<ItemUpdate>>', self.item_edited)

            # Listbox has gained focus
            lbox.bind('<FocusIn>', self.selection_changed)

            # PageUp, PageDown
            lbox.bind('<Prior>', self.page_up_down)
            lbox.bind('<Next>', self.page_up_down)

    def configure_vertical_scrollbar(self) -> None:
        """
        Set the vertical scrollbar of the inner frame to scroll all listboxes
        simultaneously.
        """
        # Set function to call when the vertical scrollbar was used
        self.inner_frame.vsb['command'] = self.vscroll

        # Attach vertical scrollbar to all listboxes so it will be moved
        # independent of the listbox that was scrolled in
        for i in range(len(self.head)):
            self.lbox[i].config(yscrollcommand=self.inner_frame.vsb.set)

    def add_data(self) -> None:
        """
        Add the given data to the table.
        """
        # Loop rows
        for row in range(len(self.data)):
            # Loop columns
            for column in range(len(self.head)):
                if self.data[row][column] is None:
                    self.data[row][column] = ''
                self.lbox[column].insert('end', self.data[row][column])

        # Save the height of a listbox item (= row height)
        if self.row_height is None:
            self.row_height = self.lbox[0].bbox(0)[1]/2+self.lbox[0].bbox(0)[3]


        # TODO: Create a method to set color for a specific cell
        # self.lbox[3].itemconfig(4, bg='yellow')
        # self.lbox[3].itemconfig(4, fg='blue')
        # self.lbox[5].itemconfig(6, bg='red')

    # noinspection PyUnusedLocal
    def change_size(self, event: tk.Event) -> None:
        """
        Callback that gets triggered by the <Configure>-Event of the canvas of
        the inner frame (= ScrollFrame). If the size of the canvas changes the
        size of the listboxes will be adjusted accordingly.

        Args:
            event: The Event object.
        """
        # Set height of the listboxes in pixels
        # listbox height = canvas height - label height - scrollbar height
        canvas_height = self.inner_frame.canvas.winfo_height()
        label_height = self.lbls[0].winfo_height()
        scrollbar_height = 15
        lbox_height = canvas_height - label_height - scrollbar_height

        # Calculate the number of visible rows of a listbox
        self.visible_rows = int(lbox_height // self.row_height)

        # Adjust listbox heights but adjusting the number of rows
        for lbox in self.lbox:
            lbox.configure(height=self.visible_rows)

    def selection_changed(self, event: tk.Event, row: int | None = None) \
        -> None:
        """
        Callback for <<ListboxSelect>>. Synchronizes the scroll position and the
        selected item of the listboxes, so that current row, column and cell are
        highlighted.

        Args:
            event: The Event object.
            row:   The row of the selected item.
        """
        # Get the scroll position of the listbox that triggered the callback
        scroll_pos = event.widget.yview()

        # Get the index of the selected item
        if row is None:
            self.current_row = event.widget.get_selected_index()
        else:
            self.current_row = row

        # Adjust scroll position, selected item and colors of each listbox
        default_bg = self.default_bg
        selected_bg = self.selected_bg
        default_fg = self.default_fg
        selected_fg = self.selected_fg

        # Loop columns
        for i in range(len(self.head)):
            padding_frame = self.padding_frames[i]
            lbl = self.lbls[i]
            lbox = self.lbox[i]

            # Set scroll position
            lbox.yview_moveto(scroll_pos[0])

            # Set selected item
            lbox.selection_clear(0, 'end')
            lbox.select_set(self.current_row)

            # Set colors of selected cell, column and row if necessary
            if event.widget == lbox:
                self.selected_cell['col'] = i

                # Selected cell
                if lbox.cget('selectbackground') != selected_bg['cell']:
                    lbox.configure(selectbackground=selected_bg['cell'])
                    lbox.configure(selectforeground=selected_fg['cell'])

                # Selected column (listbox)
                if lbox.cget('background') != selected_bg['column']:
                    padding_frame.configure(background=selected_bg['column'])
                    lbox.configure(background=selected_bg['column'])
                    lbox.configure(foreground=selected_fg['column'])

                # Selected column heading (label)
                if lbl.cget('background') != selected_bg['column_heading']:
                    # noinspection PyCallingNonCallable
                    lbl.configure(background=selected_bg['column_heading'])  # type: ignore
                    # noinspection PyCallingNonCallable
                    lbl.configure(foreground=selected_fg['column_heading'])  # type: ignore

                # Set color of highlight extension
                self.highlight_ext_frames_left[i].configure(
                    background=selected_bg['cell'])
                self.highlight_ext_frames_right[i].configure(
                    background=selected_bg['cell'])
            else:
                # Cell in same row as selected cell
                if lbox.cget('selectbackground') != selected_bg['column']:
                    lbox.configure(selectbackground=selected_bg['column'])
                    lbox.configure(selectforeground=selected_fg['column'])

                # Not selected column (listbox)
                if lbox.cget('background') != default_bg['column']:
                    padding_frame.configure(background=default_bg['column'])
                    lbox.configure(background=default_bg['column'])
                    lbox.configure(foreground=default_fg['column'])

                # Not selected column heading (label)
                if lbl.cget('background') != default_bg['column_heading']:
                    # noinspection PyCallingNonCallable
                    lbl.configure(background=default_bg['column_heading'])  # type: ignore
                    # noinspection PyCallingNonCallable
                    lbl.configure(foreground=default_fg['column_heading'])  # type: ignore

                # Set color of highlight extension
                self.highlight_ext_frames_left[i].configure(
                    background=selected_bg['column'])
                self.highlight_ext_frames_right[i].configure(
                    background=selected_bg['column'])

            # If a specific fore- and background is assigned to the cell,
            # set selectforeground and selectbackground to this color, so it
            # gets maintained
            if len(lbox.itemcget(self.current_row, 'bg')) != 0:
                lbox.configure(
                    selectbackground=lbox.itemcget(self.current_row, 'bg'))

            if len(lbox.itemcget(self.current_row, 'fg')) != 0:
                lbox.configure(
                    selectforeground=lbox.itemcget(self.current_row, 'fg'))

            # Adjust position and size of highlight extension
            self.adjust_highlight_extension_geometry(i, lbox)

    def adjust_highlight_extension_geometry(self, column_no: int,
                                            lbox: EditableListbox) -> None:
        """
        Sets the position and size of the highlight extension for the given
        column.

        Args:
            column_no: The number of the column.
            lbox:      The list box.
        """
        # Get index of selected item
        if len(lbox.curselection()) > 0:
            selected_index = lbox.curselection()[0]
        else:
            selected_index = 0

        # Get y coordinate and height of selected item
        y0 = lbox.bbox(selected_index)[1]  # type: ignore

        # Adjust position
        self.highlight_ext_frames_left[column_no]\
            .place_configure(y=y0)
        self.highlight_ext_frames_right[column_no]\
            .place_configure(y=y0, x=lbox.winfo_width() + 6)

        # Adjust height
        height = lbox.bbox(selected_index)[3]  # type: ignore
        self.highlight_ext_frames_left[column_no].configure(height=height + 1)
        self.highlight_ext_frames_right[column_no].configure(height=height + 1)

    def mouse_scroll(self, event: tk.Event) -> str | None:  # type: ignore
        """
        Callback for the <MouseWheel> event of the listboxes. Changes the scroll
        position of the focussed listbox and synchronizes it with the others.

        Args:
            event: The Event object.

        Returns:
            'break' if the operating system is Windows, otherwise None.
        """
        # Number of rows to be scrolled
        scroll_factor = 3

        # Set divisor depending on operating system
        if self.os == 'win':
            divisor = 120
        else:
            divisor = 1

        # If SHIFT key is NOT pressed scroll all listboxes
        if not event.state:
            for i in range(len(self.head)):
                self.lbox[i].yview_scroll(
                    int(-1 * (event.delta / divisor)) * scroll_factor, 'units')

        # Prevent the focussed listbox from being scrolled twice
        if self.os == 'win':
            return 'break'

    def vscroll(self, *args) -> None:
        """
        Callback that is triggered when the vertical scrollbar is used. It
        scrolls all listboxes simultaneously.

        Args:
            *args: Positional arguments.
        """
        for i in range(len(self.head)):
            self.lbox[i].yview(*args)

    def arrow_left(self, event: tk.Event) -> str:
        """
        Callback for <Left> event (left arrow key pressed) of the listboxes.
        Changes the active listbox to the next left one and scrolls
        horizontally.

        Args:
            event: The Event object

        Returns:
            'break' to suppress horizontal scrolling within the listboxes with
            arrow key.
        """
        self.change_active_listbox(event, 'left')
        self.hscroll(event, 'left')

        # Suppress horizontal scrolling within the listboxes with arrow key
        return 'break'

    def arrow_right(self, event):
        """
        Callback for <Left> event (left arrow key pressed) of the listboxes.
        Changes the active listbox to the next right one and scrolls
        horizontally.

        Args:
            event: The Event object
        """
        self.change_active_listbox(event, 'right')
        self.hscroll(event, 'right')

        # Suppress horizontal scrolling within the listboxes with arrow key
        return 'break'

    def change_active_listbox(self, event: tk.Event, side: str) -> None:
        """
        Sets focus to the next listbox on the left or right of the listbox
        that triggered this function.

        Args:
            event: The Event object.
            side:  The side of the listbox to focus ('left' or 'right').
        """
        # Loop listboxes
        for i in range(len(self.head)):
            # Listbox which triggered this event (= listbox that is active)?
            if self.lbox[i] == event.widget:
                # Get the index the selected item
                index = self.lbox[i].get_selected_index()

                # Get column number of the next listbox
                if side == 'left':
                    neighbor_column_id = i - 1
                else:
                    neighbor_column_id = i + 1

                # Check if there is a listbox on the given side
                if neighbor_column_id > len(self.head) - 1:
                    # Jump to the first column of the table
                    neighbor_column_id = 0
                elif neighbor_column_id < 0:
                    # Jump to the last column of the table
                    neighbor_column_id = len(self.head) - 1

                # Focus the next listbox on the given side
                self.lbox[neighbor_column_id].select_item(index)

    def hscroll(self, event: tk.Event, side: str) -> None:
        """
        Gets called when the arrow keys are used to select the active listbox.
        Adjusts the position of the horizontal scrollbar.

        Args:
            event: The Event object.
            side:  The side of the listbox to focus ('left' or 'right').
        """
        # Get the width of the canvas within the inner frame (visible width)
        canvas_width = self.inner_frame.canvas.winfo_width()

        # Determine the width of all listboxes and the id of the listbox that
        # triggered the callback
        width_all_lbox = 0
        event_widget_id = -1
        for i in range(len(self.head)):
            width_all_lbox += self.lbox[i].winfo_width()

            if event.widget == self.lbox[i]:
                event_widget_id = i

        # Jump to the first or last column of the table if there is no listbox
        # on the given side
        if event_widget_id == 0 and side == 'left':
            self.inner_frame.canvas.xview_moveto(1)
            return
        elif event_widget_id == len(self.head) - 1 and side == 'right':
            self.inner_frame.canvas.xview_moveto(0)
            return

        # Determine the necessary scroll position so that the active listbox
        # is visible. Differ between left and right arrow key so the scroll
        # position is only changed if the ative listbox is out of the visible
        # area of the canvas
        if side == 'right':
            # Determine width
            width = 0
            for i in range(event_widget_id + 2):
                width += self.lbox[i].winfo_width()

            # Determine necessary scroll position and adjust current scroll
            # position of the active listbox is not visible
            scroll_pos = (width - canvas_width) / width_all_lbox
            if self.inner_frame.canvas.xview()[0] < scroll_pos:
                self.inner_frame.canvas.xview_moveto(scroll_pos)
        else:
            # Erforderliche Breite ermitteln
            width = width_all_lbox
            for i in range(len(self.head) - 1, event_widget_id - 2, -1):
                width -= self.lbox[i].winfo_width()

            # Determine necessary scroll position and adjust current scroll
            # position of the active listbox is not visible
            scroll_pos = width / width_all_lbox
            if self.inner_frame.canvas.xview()[0] > scroll_pos:
                self.inner_frame.canvas.xview_moveto(scroll_pos)

    def item_edited(self, event: tk.Event) -> None:
        """
        Callback that is triggered when a cell (listbox item) was edited.
        Determines the row and column of the edited item and adjusts the data
        model.

        Args:
            event: The Event object
        """
        # Get row id (= index of the listbox item)
        row = event.widget.get_selected_index()

        # Get column id (= listbox id of the item)
        column = -1
        for i in range(len(self.head)):
            # Listbox which triggered the callback?
            if self.lbox[i] == event.widget:
                column = i

        # Get the new value of the cell/listbox item
        new_text = self.lbox[column].get(row)

        # Update data model
        self.data[row][column] = new_text

        # Debugging: Print updated cell and new value
        print(f'Geändert wurde Zeile: {row}, Spalte: {column}')
        print(f'Neuer Text: \"{new_text}\"')

    def label_mouse_motion(self, event: tk.Event) -> None:
        """
        Callback that is triggered if the cursor is over a label of the table
        head. Changes the symbol if the cursor is on the right end of the label.

        Args:
            event: The Event object.
        """
        # Get label width and cursor position
        label_width = event.widget.winfo_width()
        cursor_x = event.x

        # Prüfen, ob der Maus-Zeiger sich am rechten Ende des Labels befindet.
        # Wenn ja, Cursor ändern, Toleranz = 20 px

        # Check if cursor is on the right side of the label (tolerance = 20 px)
        # If yes change cursor symbol
        toleranz = 20
        if label_width - toleranz <= cursor_x:
            event.widget.config(cursor='right_side')
        else:
            event.widget.config(cursor='')

    def label_b1_mouse_motion(self, event: tk.Event) -> None:
        """
        Callback that is triggered if the cursor is moved within a label of
        the table head with the left mouse button pressed. Changes the width
        of the column/listbox according to the cursor position.

        Args:
            event: The Event object
        """
        column_no: int = -1

        # Label which triggered the event
        lbl = event.widget

        # Get instance of the label
        for lbl_frm in self.lbls:
            if lbl == lbl_frm.wdg:
                lbl: FramedWidget = lbl_frm    # type: ignore
                column_no = self.lbls.index(lbl_frm)
                break

        # Get mouse position (coordinate system of the label)
        maus_x = event.x

        # Adjust column width by changing ipadx of the grid.
        # lbl.configure(width=xxx) is not possible because the paramter is
        # the width in number of characters not pixels!
        ipadx = (maus_x - lbl.winfo_reqwidth()) / 2
        if ipadx >= 0:
            lbl.grid(ipadx=ipadx)

        # Adjust position and size of highlight extension
        self.adjust_highlight_extension_geometry(column_no,
                                                 self.lbox[column_no])

    def set_focus(self) -> None:
        """
        Sets focus to the active listbox.
        """
        self.lbox[self.selected_cell['col']].focus_set()

    def page_up_down_old(self, event: tk.Event) -> str:
        """
        Callback for the PageUp and PageDown keys that ensured correct behavior
        of the table.

        Args:
            event: The Event object.

        Returns:
            'break' to prevent the listbox from being scrolled twice.
        """
        # Calculate new index
        max_index = len(self.data) - 1
        if event.keysym == 'Prior':
            new_index = max(self.current_row - self.visible_rows, 0)
        elif event.keysym == 'Next':
            new_index = min(self.current_row + self.visible_rows - 1, max_index)
        else:
            new_index = 0

        # Set selected listbox item
        lbox: EditableListbox = event.widget
        lbox.select_item(new_index)

        # Workaround to ensure correct scroll position
        if new_index == 0:
            lbox.event_generate('<Down>')
            lbox.event_generate('<Up>')
        else:
            lbox.event_generate('<Up>')
            lbox.event_generate('<Down>')

        # Prevent the listbox from being scrolled twice
        return 'break'

    def page_up_down(self, event: tk.Event) -> str:
        """
        Callback for the PageUp and PageDown keys that ensured correct behavior
        of the table.

        Args:
            event: The Event object.

        Returns:
            'break' to prevent the listbox from being scrolled twice.
        """
        # Calculate new index
        max_index = len(self.data) - 1
        if event.keysym == 'Prior':
            new_index = max(self.current_row - self.visible_rows, 0)
        elif event.keysym == 'Next':
            new_index = min(self.current_row + self.visible_rows - 1, max_index)
        else:
            new_index = 0

        # Go up or down by number of visible items - 1
        lbox: EditableListbox = event.widget
        if new_index < self.current_row:
            key = 'Up'
            rng = range(self.current_row, new_index + 1, -1)
        else:
            key = 'Down'
            rng = range(self.current_row, new_index)

        for i in rng:
            lbox.event_generate(f'<{key}>')

        # Prevent the listbox from being scrolled twice
        return 'break'
