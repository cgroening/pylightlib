"""
pylightlib.platform.windows
===========================

Windows-specific utilities for improving Tkinter UI behavior on
high-DPI displays.

Author:
    Corvin Gröning

Date:
    2025-03-22

Version:
    0.1

This module contains Windows-specific functionality for the PyLight GUI
framework. Currently, it provides a workaround for blurry fonts in Tkinter on
high-DPI displays by adjusting the scaling factor using native Windows API calls
via `ctypes`.

It defines the `PyLightTk_Windows` class with static methods that can be called
during application setup to ensure consistent UI scaling and sharper font
rendering on modern displays.
"""


# Libs
from ctypes import windll  # type: ignore


class PyLightTk_Windows:
    """
    This class contains methods for the operating system Windows.
    """

    @staticmethod
    def high_dpi_scaling(tkroot):
        """
        On high resolution screens the font is blurry when using Tkinter. This
        method is a workaround to achieve sharp fonts.

        Args:
            tkroot: Tkinter root object.
        """
        # Get scaling value from system settings in % and create scaling factor
        scaling = windll.shcore.GetScaleFactorForDevice(0) / 100 * 1.5

        # Set scaling factor for tk window
        tkroot.call('tk', 'scaling', scaling)
        windll.shcore.SetProcessDpiAwareness(1)
