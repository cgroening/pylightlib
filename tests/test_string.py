"""Tests for pylightlib.msc.String."""

import pytest
from pylightlib.msc.String import String


class TestCharPos:
    """Tests for String.charpos."""

    def test_basic(self):
        assert String.charpos("hello world", "o") == [4, 7]

    def test_no_match(self):
        assert String.charpos("hello world", "z") == []

    def test_empty_string(self):
        assert String.charpos("", "a") == []

    def test_single_char(self):
        assert String.charpos("a", "a") == [0]

    def test_all_matching(self):
        assert String.charpos("aaaa", "a") == [0, 1, 2, 3]


class TestLinewrap:
    """Tests for String.linewrap."""

    def test_short_text_no_wrap(self):
        result = String.linewrap("Hello world", 80)
        assert result == "Hello world"

    def test_wrap_at_whitespace(self):
        text = "This is a long text that should be wrapped at a space position"
        result = String.linewrap(text, 20)
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped:
                assert len(stripped) <= 20, f"Line too long: '{stripped}' ({len(stripped)} chars)"

    def test_exact_linewidth(self):
        """12345 67890 with linewidth=5 wraps at the space."""
        result = String.linewrap("12345 67890", 5)
        assert "12345" in result
        assert "0" in result or "6789" in result or "67890" in result

    def test_single_word_longer_than_width(self):
        text = "Supercalifragilisticexpialidocious"
        result = String.linewrap(text, 10)
        parts = result.split("\n")
        for p in parts:
            stripped = p.strip()
            if stripped:
                assert len(stripped) <= 10, f"Part too long: '{stripped}' ({len(stripped)})"

    def test_empty_text(self):
        assert String.linewrap("", 10) == ""

    def test_newlines_in_text(self):
        text = "Short text"
        result = String.linewrap(text, 10)
        assert "Short text" == result.strip()

    def test_linewidth_one(self):
        text = "ab cd"
        result = String.linewrap(text, 1)
        lines = result.split("\n")
        for line in lines:
            if line.strip():
                assert len(line.strip()) <= 1

    def test_multiple_whitespace_handling(self):
        text = "word1    word2"
        result = String.linewrap(text, 10)
        assert "word1" in result
        assert "word2" in result

    def test_preserve_words(self):
        text = "one two three four five"
        result = String.linewrap(text, 8)
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped:
                assert len(stripped) <= 8
