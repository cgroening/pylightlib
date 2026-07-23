"""Tests for pylightlib.io.Textfile."""

import os
import tempfile
import pytest
from pylightlib.io.Textfile import Textfile


class TestTextfile:
    """Tests for Textfile read/write operations."""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file with known content."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            f.write("line1\nline2\nline3\n")
            f.flush()
            path = f.name
        yield path
        os.unlink(path)

    def test_readlines(self, temp_file):
        lines = Textfile.readlines(temp_file)
        assert lines == ["line1\n", "line2\n", "line3\n"]

    def test_read(self, temp_file):
        content = Textfile.read(temp_file)
        assert content == "line1\nline2\nline3\n"

    def test_write(self, temp_file):
        Textfile.write(temp_file, "new content")
        content = Textfile.read(temp_file)
        assert content == "new content"

    def test_write_overwrites(self, temp_file):
        Textfile.write(temp_file, "first write")
        Textfile.write(temp_file, "second write")
        content = Textfile.read(temp_file)
        assert content == "second write"

    def test_read_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            path = f.name
        try:
            content = Textfile.read(path)
            assert content == ""
        finally:
            os.unlink(path)

    def test_write_and_read_back(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            path = f.name
        try:
            Textfile.write(path, "test content 123")
            content = Textfile.read(path)
            assert content == "test content 123"
        finally:
            os.unlink(path)
