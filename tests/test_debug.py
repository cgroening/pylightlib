"""Tests for pylightlib.msc.Debug."""

import io
import sys
import pytest
from pylightlib.msc.Debug import Debug


class TestPrintArguments:
    """Tests for Debug.print_arguments decorator."""

    def test_basic_call(self):
        @Debug.print_arguments
        def add(a, b):
            return a + b

        # Capture stdout
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            result = add(3, 5)
        finally:
            sys.stdout = old_stdout

        assert result == 8
        output = captured.getvalue()
        assert "add" in output
        assert "Args" in output or "called" in output

    def test_with_kwargs(self):
        @Debug.print_arguments
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            result = greet("World", greeting="Hi")
        finally:
            sys.stdout = old_stdout

        assert result == "Hi, World!"
        output = captured.getvalue()
        assert "greet" in output

    def test_no_args(self):
        @Debug.print_arguments
        def constant():
            return 42

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            result = constant()
        finally:
            sys.stdout = old_stdout

        assert result == 42


class TestTiming:
    """Tests for Debug.timing decorator."""

    def test_timing_seconds(self):
        @Debug.timing(use_ns_timer=False)
        def quick():
            return 1

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            result = quick()
        finally:
            sys.stdout = old_stdout

        assert result == 1
        output = captured.getvalue()
        assert "took" in output
        assert "s" in output or "ns" in output

    def test_timing_nanoseconds(self):
        @Debug.timing(use_ns_timer=True)
        def quick():
            return 1

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            result = quick()
        finally:
            sys.stdout = old_stdout

        assert result == 1
        output = captured.getvalue()
        assert "ns" in output

    def test_keeps_function_name(self):
        @Debug.timing()
        def my_special_func():
            pass

        assert my_special_func.__name__ == "my_special_func"

    def test_keeps_function_name_print_args(self):
        @Debug.print_arguments
        def my_other_func():
            pass

        assert my_other_func.__name__ == "my_other_func"
