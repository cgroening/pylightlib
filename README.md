# PyLightLib

**PyLightLib** is a modular Python library designed to simplify GUI development (with `tkinter` and `PyQt`), TUI development with `Textual` data storage, debugging and utility functions for everyday development tasks.

## 📦 Installation

```bash
pip install git+https://github.com/cgroening/pylightlib.git
```

Or install locally:

```bash
git clone https://github.com/cgroening/pylightlib.git
cd pylightlib
pip install .
```

## 🧱 Structure & Modules

The library is organized into several submodules, each serving a specific purpose.

### `io` – File and Storage Operations
Simplified file handling and persistent storage:
- `AppStorage`: Application configuration storage.
- `Database`: Wrapper for SQLite database operations.
- `File`: Filesystem operations (e.g., paths, copying).
- `Textfile`: Read and write text files.

### `msc` – Miscellaneous Utilities
General-purpose helpers:
- `Debug`: Decorators for logging and measuring function execution time.
- `DateTime`: Date and time utilities.
- `String`: String helper functions.
- `Singleton`: Basic singleton class.
- `SysPathHandler`: Manage and manipulate `sys.path`.

### `qt` – Qt GUI Widgets
Extensions and helpers for PyQt5/PySide2:
- `CustomDateEdit`: QDateEdit widget with support for empty values and flexible date handling.
- `CustomMessageBox`: Custom wrapper around QMessageBox for simple info and confirmation dialogs.
- `DatePickerDialog`: Simple dialog window with a calendar-based date picker.
- `FnButtonsFrame`: Function key bar with modifier support (child of QFrame).
- `LinkLabel`: Clickable QLabel that opens a URL when clicked.
- `StatusMessage`: Helper to display timestamped messages in a QStatusBar.
- `StyleSheet`: Utility class for processing .css files with variable support and light/dark mode handling.
- `TableHelper`: Utility class to populate and manage QTableWidget with structured data.

### `tk` – Tkinter GUI Components
Custom widgets and views:
- `AboutView`: View class for displaying application information in a simple about window.
- `DefaultColorScheme`: Design templates for consistent UI.
- `EditableListbox`: A custom Tkinter Listbox widget with inline editing functionality.
- `FnButtonFrame`: A module for managing customizable function key widgets (F1–F12) in a graphical user interface using Tkinter.
- `FramedWidget`: A customizable frame wrapper for standard Tkinter and ttk widgets with configurable borders and focus-based highlighting.
- `PyLightTk_Windows`: Windows-specific utilities for improving Tkinter UI behavior on high-DPI displays.
- `PyLightWindow`: Tkinter-based application window with color scheme, DPI support, and persistent layout saving.
- `ScrollFrame`: A reusable scrollable frame for embedding widgets in Tkinter GUIs.
- `ScrollTextBox`: A scrollable text box widget using Tkinter and ttk.
- `Table`: A fully scrollable, editable and styleable table widget for Tkinter GUIs.
- `ViewBase`: Abstract base class for all application views using the PyLightWindow framework.

### `txtl` – Text & Terminal Utilities
- `CustomBindings`: Manage Keyboard binding configuration
- `CustomDataTable`: Custom `DataTable` with flexible column widths
- `QuestionScreen`: Modal screen component for confirming user decisions
via Yes/No buttons.