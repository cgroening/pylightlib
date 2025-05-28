"""
pylightlib.txtl.QuestionScreen
=======================

A reusable modal screen component for confirming user decisions
via Yes/No buttons.

Author:
    Corvin Gröning

Date:
    2025-05-24

Version:
    0.1


This module defines `QuestionScreen`, a subclass of `ModalScreen`
in the Textual framework, designed to present a question to the user and
collect a simple boolean response.

The screen displays a customizable question and two buttons labeled "Yes"
and "No". It uses Textual's event system to handle user interactions and
returns `True` or `False` accordingly. The button colors can be configured using
the `ButtonColor` enum, allowing visual emphasis (e.g., marking "Yes" as
destructive in red or "No" as a safe action in blue).

The screen can be dismissed using the escape key or by clicking a button. It is
ideal for confirmation dialogs, safety prompts or binary decision points within
an application UI.
"""
from enum import Enum

from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual import on


class ButtonColor(Enum):
    """
    Enum for button colors.
    """
    DEFAULT = 'default'
    PRIMARY = 'primary'
    ERROR = 'error'
    SUCCESS = 'success'
    WARNING = 'warning'


class QuestionScreen(ModalScreen[bool]):
    """
    A screen that asks a question and returns the answer as a boolean value.
    """
    yes_button_color: ButtonColor
    no_button_color: ButtonColor
    BINDINGS = [
        ('escape', 'close_modal', 'Close'),
    ]
    CSS = """
        QuestionScreen {
            align: center middle;
        }

        QuestionScreen #dialog {
            grid-size: 2;
            grid-gutter: 1 2;
            grid-rows: 1fr 3;
            padding: 0 1;
            width: 60;
            height: 11;
            border: thick $background 80%;
            background: $surface;
        }

        QuestionScreen #question {
            column-span: 2;
            height: 1fr;
            width: 1fr;
            content-align: center middle;
        }

        QuestionScreen Button {
            width: 100%;
        }
    """


    def __init__(self, question: str,
                 yes_button_color: ButtonColor = ButtonColor.ERROR,
                 no_button_color: ButtonColor = ButtonColor.PRIMARY) -> None:
        """
        Initialize the QuestionScreen with a question.
        """
        self.question = question
        self.yes_button_color = yes_button_color
        self.no_button_color = no_button_color
        super().__init__()

    def compose(self) -> ComposeResult:
        """
        Compose the screen layout.
        """
        yield Grid(
            Label(self.question, id='question'),
            Button('Yes', variant=self.yes_button_color.value, id='yes'),
            Button('No', variant=self.no_button_color.value, id='no'),
            id='dialog',
        )

    def action_close_modal(self) -> None:
        """
        Closes the modal popup.
        """
        self.app.pop_screen()

    @on(Button.Pressed, '#yes')
    def handle_yes(self) -> None:
        """
        Handle the "Yes" button press.
        """
        self.dismiss(True)

    @on(Button.Pressed, '#no')
    def handle_no(self) -> None:
        """
        Handle the "No" button press.
        """
        self.dismiss(False)
