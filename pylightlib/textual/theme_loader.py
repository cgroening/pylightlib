import logging
import importlib
import os
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from textual.app import App
from textual.theme import Theme


DEFAULT_PYLIGHT_THEME_PREFIX = 'pyl_'
DEFAULT_CUSTOM_THEME_PREFIX = 'custom_'
SCRIPT_DIR = Path(__file__).parent.parent
STANDARD_THEMES_DIR = SCRIPT_DIR / 'textual/standard_themes'


@dataclass(frozen=False, slots=True)
class ThemeData:
    """
    Data class to hold theme information.

    Attributes
    ----------
    name : str
        The name of the theme.
    prefix : str
        The prefix for the theme.
    textual_theme : Theme
        The Textual theme instance.
    css_files : list[str] or None, optional
        List of CSS file paths associated with the theme, by default None.
    """
    name: str
    prefix: str
    textual_theme: Theme
    css_files: list[str] | None = None


class ThemeLoader:
    """
    A class to load and manage themes for applications using the Textual.

    The themes are expected to be in subfolder of the `themes` directory,
    each containing a `theme.py` file defining a `TEXTUAL_THEME` variable.
    Additionally, any number of `.css` files can be included in the
    theme folder.

    This class dynamically imports the theme modules, registers them and makes
    them available for use in the application.

    Attributes
    ----------
    THEME_FOLDER : str | None
        The path to the theme folder.
    PYLIGHT_THEME_PREFIX : str
        The prefix for themes included with pylightlib.
    CUSTOM_THEME_PREFIX : str
        The prefix for custom themes.
    THEME_NAMES : list[str]
        A list of available theme names.
    THEME_DATA : dict[str, ThemeData]
        A dictionary mapping theme names to their data.

    Methods
    -------
    get_previously_used_theme(theme_config_file, default_theme_name)
        Return the name of the previously used theme from config file.
    register_themes_in_textual_app(app)
        Register all loaded themes in the given Textual application.
    set_previous_theme_in_textual_app(app, default_theme_name, theme_config_file)
        Set the previously used theme in the given Textual application.
    save_theme_to_config(theme_name, theme_config_file)
        Save the name of the active theme to the config file.
    load_theme_css(theme_name, app)
        Load the CSS files for the current theme.
    change_to_next_or_previous_theme(direction, app)
        Change to the next or previous theme in the list.
    """
    THEME_FOLDER: str | None
    PYLIGHT_THEME_PREFIX: str
    CUSTOM_THEME_PREFIX: str
    THEME_NAMES: list[str] = []
    THEME_DATA: dict[str, ThemeData] = {}


    def __init__(
        self, theme_folder: str | None = None,
        pylight_theme_prefix: str = DEFAULT_PYLIGHT_THEME_PREFIX,
        custom_theme_prefix: str = DEFAULT_CUSTOM_THEME_PREFIX,
        include_standard_themes: bool = True
    ) -> None:
        """
        Initialize the ThemeLoader and load themes from the themes directory.

        Parameters
        ----------
        theme_folder : str | None
            The path to the folder containing theme directories. If the value
            is None, the default "themes" directory is used.
        pylight_theme_prefix : str
            The prefix for themes included with pylightlib.
        custom_theme_prefix : str
            The prefix for custom themes.
        include_standard_themes : bool, optional
            If True, load standard themes as well.
        """
        self.THEME_FOLDER = theme_folder
        self.PYLIGHT_THEME_PREFIX = pylight_theme_prefix
        self.CUSTOM_THEME_PREFIX = custom_theme_prefix
        if include_standard_themes:
            self._load_themes(standard_themes=include_standard_themes)
        self._load_themes()  # Custom themes
        self.THEME_NAMES.sort()

    def _load_themes(self, standard_themes: bool = False) -> None:
        """
        Load themes from the "themes" directory.

        This method scans the themes directory for valid theme folders,
        imports their theme modules, and registers them for use.

        Parameters
        ----------
        standard_themes : bool, optional
            If True, load standard themes; otherwise, load custom themes.
        """
        # Loop all items in the themes folder
        if standard_themes:
            sys.path.append(str(Path(__file__).parent))
            theme_folder_name = 'standard_themes'
            prefix = self.PYLIGHT_THEME_PREFIX
        else:
            if not self.THEME_FOLDER:
                return
            parent_path = Path(self.THEME_FOLDER).parent
            sys.path.append(f'{parent_path}')
            theme_folder_name = Path(self.THEME_FOLDER).name
            prefix = self.CUSTOM_THEME_PREFIX

        # Import the parent theme folder to get its path
        try:
            themes_parent_folder = __import__(theme_folder_name).__path__[0]
        except ModuleNotFoundError:
            logging.warning(
                f'Theme folder "{theme_folder_name}" not found. Skipping.'
            )
            return

        for item in os.listdir(themes_parent_folder):
            full_path = os.path.join(themes_parent_folder, item)

            # Skip if name begins with "." or "_"; skip non-folders
            if item.startswith('.') or item.startswith('_') \
            or not os.path.isdir(full_path):
                continue

            # Dynamically import the theme module
            module_name = f'{theme_folder_name}.{item}.theme'
            self._import_and_register_theme(
                item, prefix, module_name, full_path
            )

        logging.info(
            f'Found {len(self.THEME_NAMES)} themes in "{themes_parent_folder}"'
        )

    def _get_css_files_for_theme(self, theme_folder_path: str) -> list[str]:
        """
        Generate a list of CSS files in the given folder.

        Parameters
        ----------
        theme_folder_path : str
            The path to the theme folder.

        Returns
        -------
        list[str]
            A list of CSS file paths.
        """
        css_files = []
        for file_name in os.listdir(theme_folder_path):
            if file_name.endswith('.css'):
                css_files.append(os.path.join(theme_folder_path, file_name))
        return css_files

    def _import_and_register_theme(
        self, theme_name: str, prefix: str, module_name: str, full_path: str
    ) -> None:
        """
        Import a theme module and register its theme.

        Parameters
        ----------
        theme_name : str
            The name of the theme.
        prefix : str
            The prefix to add to the theme name when registering.
        module_name : str
            The module name to import.
        full_path : str
            The full path to the theme folder.

        Raises
        ------
        ModuleNotFoundError
            If the theme module cannot be imported.
        Exception
            If any other error occurs during theme loading.
        """
        try:
            # Import the theme module (theme.py)
            theme_module = importlib.import_module(module_name)
            textual_theme = getattr(theme_module, 'TEXTUAL_THEME', None)
            css_files = self._get_css_files_for_theme(full_path)

            # Abort if no TEXTUAL_THEME variable is defined
            if textual_theme is None:
                logging.warning(
                    f'Skipping theme "{theme_name}" (no TEXTUAL_THEME defined)'
                )
                return

            # Register the theme
            self._save_theme_data(theme_name, prefix, textual_theme, css_files)
            logging.info(f'Registered theme: {theme_name}')
        except ModuleNotFoundError:
            logging.warning(f'Skipping theme "{theme_name}" (no theme.py)')
        except Exception as e:
            logging.error(f'Error loading theme "{theme_name}": {e}')

    def _save_theme_data(
        self, name: str,
        prefix: str,
        theme_instance: Theme,
        css_files: list[str] | None = None
    ) -> None:
        """
        Save the theme data into the THEME_DATA dictionary and add the theme
        name to the list of all names.

        Parameters
        ----------
        name : str
            The name of the theme.
        prefix : str
            The prefix to add to the theme name when registering.
        theme_instance : Theme
            The Textual theme instance.
        css_files : list[str] or None, optional
            List of CSS file paths, by default None.
        """
        self.THEME_NAMES.append(name)
        self.THEME_DATA[name] = ThemeData(
            name=name,
            prefix=prefix,
            textual_theme=theme_instance,
            css_files=css_files
        )

    def get_previously_used_theme(
        self, theme_config_file: Path, default_theme_name: str
    ) -> str:
        """
        Return the name of the previously used theme from the config file.

        Parameters
        ----------
        theme_config_file : Path
            Path to the config file.
        default_theme_name : str
            The default theme name to return if no previous theme is found.

        Returns
        -------
        str
            The theme name.

        Raises
        ------
        json.JSONDecodeError
            If the config file contains invalid JSON.
        IOError
            If there's an error reading the config file.
        """
        if theme_config_file.exists():
            try:
                with open(theme_config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('theme', theme_config_file)
            except (json.JSONDecodeError, IOError):
                return default_theme_name
        return default_theme_name

    def register_themes_in_textual_app(self, app: App) -> None:
        """
        Register all loaded themes in the given Textual application.

        Parameters
        ----------
        app : App
            The instance of the Textual application.
        """
        # Sort themes, first PYLIGHT_THEME_PREFIX, then CUSTOM_THEME_PREFIX
        self.THEME_NAMES.sort( key=lambda name: (
            0 if self.THEME_DATA[name].prefix == self.PYLIGHT_THEME_PREFIX else 1,
            name
        ) )

        # Loop through name list instead of dict to keep alphabetic order
        for theme_name in self.THEME_NAMES:
            theme_data = self.THEME_DATA[theme_name]
            theme_data.textual_theme.name = \
                f'{theme_data.prefix}{theme_data.textual_theme.name}'
            app.register_theme(theme_data.textual_theme)

    def set_previous_theme_in_textual_app(
        self, app: App, default_theme_name: str, theme_config_file: Path
    ) -> None:
        """
        Set the previously used theme in the given Textual application.

        Parameters
        ----------
        app : App
            The instance of the Textual application.
        default_theme_name : str
            The default theme name to use if no previous theme is found.
        theme_config_file : Path
            Path to the config file containing the previous theme.
        """
        theme_name = self.get_previously_used_theme(
            theme_config_file, default_theme_name
        )
        if theme_name in app.available_themes:
            app.theme = theme_name

        logging.info(f'Set previous theme: {theme_name}')

    def save_theme_to_config(
        self, theme_name: str, theme_config_file: Path
    ) -> None:
        """
        Save the name of the active theme to the config file.

        Parameters
        ----------
        theme_name : str
            The name of the theme to save.
        theme_config_file : Path
            The path to the config file where the theme name will be saved.

        Raises
        ------
        IOError
            If there's an error writing to the config file.
        """
        try:
            with open(theme_config_file, 'w') as f:
                json.dump({'theme': theme_name}, f)
        except IOError as e:
            logging.error(f"Could not save theme config: {e}")

    def load_theme_css(self, theme_name: str, app: App) -> None:
        """
        Load the CSS files for the current theme.

        Parameters
        ----------
        theme_name : str
            The name of the theme to load.
        app : App
            The instance of the Textual application.
        """
        # Remove CSS from previous theme
        self._remove_all_theme_css(app)

        # Remove any prefixes
        clean_name = theme_name
        for prefix in [self.PYLIGHT_THEME_PREFIX, self.CUSTOM_THEME_PREFIX]:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):]
                break

        # Load all CSS files that are in folder themes/{theme_name}/
        theme_data = self.THEME_DATA.get(clean_name)
        if not theme_data or not theme_data.css_files:
            logging.warning(f'No CSS files found for theme: {clean_name}')
            return

        for css_file in theme_data.css_files:
            try:
                app.stylesheet.read(str(css_file))
                logging.debug(f'Loaded CSS file: {css_file}')
            except Exception as e:
                logging.error(f'Error loading CSS file {css_file}: {e}')

        # Re-parse and apply to make sure changes take effect
        app.stylesheet.reparse()
        try:
            app.stylesheet.update(app.screen)
        except Exception as e:
            logging.error(f'Error updating stylesheet: {e}')

    def _remove_all_theme_css(self, app: App) -> None:
        """
        Remove all CSS files that were loaded from the /themes/ folder.

        This is necessary when switching themes to avoid conflicts
        between styles from different themes.

        Parameters
        ----------
        app : App
            The instance of the Textual application.
        """
        themes_dir = STANDARD_THEMES_DIR.resolve()

        logging.debug(f'Removing CSS files from themes directory: {themes_dir}')

        for key in list(app.stylesheet.source.keys()):
            path_str, _ = key
            try:
                css_path = Path(path_str).resolve()
            except Exception:
                continue

            # Check if the CSS file is inside the themes directory
            if themes_dir in css_path.parents:
                del app.stylesheet.source[key]

    def change_to_next_or_previous_theme(
        self, direction: int, app: App
    ) -> None:
        """
        Change to the next or previous theme in the list.

        Parameters
        ----------
        direction : int
            1 for next theme, -1 for previous theme.
        app : App
            The instance of the Textual application.
        """
        themes = list(app.available_themes)
        current_index = themes.index(app.theme)
        next_index = (current_index + direction) % len(themes)
        app.theme = themes[next_index]
