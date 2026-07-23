"""Tests for pylightlib.msc.DateTime."""

import pytest
from pylightlib.msc.DateTime import DateTime


class TestTimestampToDate:
    """Tests for DateTime.timestamp_to_date."""

    def test_known_timestamp(self):
        # 2024-01-15 12:00:00 UTC
        ts = 1705320000
        result = DateTime.timestamp_to_date(ts)
        assert result == "15.01.2024"

    def test_english_format(self):
        ts = 1705320000
        result = DateTime.timestamp_to_date(ts, english_format=True)
        assert result == "2024-01-15"

    def test_none_timestamp(self):
        assert DateTime.timestamp_to_date(None) == ""

    def test_float_timestamp(self):
        # Should return empty string since isinstance check fails for float
        assert DateTime.timestamp_to_date(3.14) == ""


class TestDateToTimestamp:
    """Tests for DateTime.date_to_timestamp."""

    def test_known_date(self):
        result = DateTime.date_to_timestamp("15.01.2024")
        assert isinstance(result, int)

    def test_english_format(self):
        result = DateTime.date_to_timestamp("2024-01-15", english_format=True)
        assert isinstance(result, int)

    def test_invalid_date(self):
        result = DateTime.date_to_timestamp("not-a-date")
        assert result is None

    def test_wrong_format(self):
        # German format given but english expected
        result = DateTime.date_to_timestamp("15.01.2024", english_format=True)
        assert result is None

    def test_wrong_format_reverse(self):
        result = DateTime.date_to_timestamp("2024-01-15")
        assert result is None


class TestDateDiff:
    """Tests for DateTime.date_diff.

    date_diff(t1, t2) computes t1 - t2 in days.
    """

    def test_zero_diff(self):
        ts = 1700000000
        assert DateTime.date_diff(ts, ts) == 0

    def test_one_day_diff(self):
        ts1 = 1700000000
        ts2 = 1700086400  # ~1 day later than ts1
        # ts1 - ts2 should be negative (ts1 is earlier)
        assert DateTime.date_diff(ts1, ts2) == -1

    def test_negative_diff(self):
        ts1 = 1700000000
        ts2 = 1699913600  # ~1 day earlier than ts1
        # ts1 - ts2 should be positive (ts1 is later)
        assert DateTime.date_diff(ts1, ts2) == 1

    def test_large_diff(self):
        ts1 = 1700000000
        ts2 = 1600000000  # ~1157 days earlier
        diff = DateTime.date_diff(ts1, ts2)
        assert diff == 1157


class TestToday:
    """Tests for DateTime.today_timestamp and today_date."""

    def test_today_timestamp_is_int(self):
        ts = DateTime.today_timestamp()
        assert isinstance(ts, int)
        assert ts > 0

    def test_today_timestamp_midnight(self):
        ts = DateTime.today_timestamp()
        assert ts % 86400 == 0

    def test_today_date_string(self):
        date_str = DateTime.today_date()
        assert isinstance(date_str, str)
        assert len(date_str) == 10  # DD.MM.YYYY
        parts = date_str.split(".")
        assert len(parts) == 3

    def test_today_date_english(self):
        date_str = DateTime.today_date(english_format=True)
        assert isinstance(date_str, str)
        assert len(date_str) == 10
        parts = date_str.split("-")
        assert len(parts) == 3
