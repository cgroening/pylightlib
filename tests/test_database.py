"""Tests for pylightlib.io.Database."""

import pytest
from pylightlib.io.Database import (
    Database,
    Condition,
    ColumnOrder,
    SQLComparisonOperator,
    SQLCombinationOperator,
    SQLOrderByDirection,
)


class TestDatabase:
    """Tests for Database using in-memory SQLite."""

    @pytest.fixture
    def db(self):
        """Create an in-memory database with a test table that has an id column."""
        database = Database(":memory:")
        database.query(
            "CREATE TABLE IF NOT EXISTS test_table ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  name TEXT NOT NULL,"
            "  value INTEGER"
            ")"
        )
        yield database
        database.close()

    def test_insert_and_fetch(self, db):
        inserted = db.insert("test_table", [{"name": "alpha", "value": 10}])
        assert len(inserted) == 1
        assert inserted[0]["name"] == "alpha"
        assert inserted[0]["value"] == 10

    def test_insert_multiple(self, db):
        data = [
            {"name": "alpha", "value": 10},
            {"name": "beta", "value": 20},
            {"name": "gamma", "value": 30},
        ]
        inserted = db.insert("test_table", data)
        assert len(inserted) == 3

        rows = db.fetch("test_table")
        assert len(rows) == 3

    def test_fetch_with_conditions(self, db):
        db.insert("test_table", [
            {"name": "alpha", "value": 10},
            {"name": "beta", "value": 20},
            {"name": "gamma", "value": 30},
        ])
        cond = Condition("value", SQLComparisonOperator.GE, 20)
        rows = db.fetch("test_table", conditions=[cond])
        assert len(rows) == 2
        assert rows[0]["name"] == "beta"

    def test_fetch_with_orderby(self, db):
        db.insert("test_table", [
            {"name": "alpha", "value": 30},
            {"name": "beta", "value": 10},
            {"name": "gamma", "value": 20},
        ])
        order = ColumnOrder("value", SQLOrderByDirection.DESC)
        rows = db.fetch("test_table", orderby=[order])
        assert rows[0]["name"] == "alpha"
        assert rows[-1]["name"] == "beta"

    def test_fetch_with_limit(self, db):
        db.insert("test_table", [
            {"name": "a", "value": 1},
            {"name": "b", "value": 2},
            {"name": "c", "value": 3},
        ])
        rows = db.fetch("test_table", limit=2)
        assert len(rows) == 2

    def test_update(self, db):
        db.insert("test_table", [{"name": "alpha", "value": 10}])
        cond = Condition("name", SQLComparisonOperator.EQ, "alpha")
        db.update("test_table", [
            {"name": "alpha_updated", "value": 99, "@conds": [cond]}
        ])
        rows = db.fetch("test_table")
        assert rows[0]["name"] == "alpha_updated"
        assert rows[0]["value"] == 99

    def test_remove(self, db):
        db.insert("test_table", [
            {"name": "keep", "value": 1},
            {"name": "remove", "value": 2},
        ])
        cond = Condition("name", SQLComparisonOperator.EQ, "remove")
        db.remove("test_table", [cond])
        rows = db.fetch("test_table")
        assert len(rows) == 1
        assert rows[0]["name"] == "keep"

    def test_context_manager(self):
        """Database with a table that has an id column."""
        db = Database(":memory:")
        db.query(
            "CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, x INTEGER)"
        )
        db.close()
        # Test basic context manager
        with Database(":memory:") as d:
            d.query("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, x INTEGER)")
            inserted = d.insert("t", [{"x": 42}])
            assert len(inserted) == 1
            assert inserted[0]["x"] == 42

    def test_custom_query(self, db):
        db.insert("test_table", [{"name": "test", "value": 100}])
        cursor = db.query("SELECT COUNT(*) AS cnt FROM test_table")
        row = cursor.fetchone()
        assert row["cnt"] >= 1

    def test_insert_with_id_autoincrement(self, db):
        inserted = db.insert("test_table", [{"name": "first", "value": 1}])
        assert inserted[0]["id"] == 1
        inserted = db.insert("test_table", [{"name": "second", "value": 2}])
        assert inserted[0]["id"] == 2


class TestCondition:
    """Tests for the Condition dataclass."""

    def test_default_combination(self):
        c = Condition("col", SQLComparisonOperator.EQ, 5)
        assert c.combination == SQLCombinationOperator.AND

    def test_equality(self):
        c1 = Condition("a", SQLComparisonOperator.EQ, 1)
        c2 = Condition("a", SQLComparisonOperator.EQ, 1)
        assert c1 == c2

    def test_different_operator(self):
        c = Condition("age", SQLComparisonOperator.GE, 18)
        assert c.operator == SQLComparisonOperator.GE


class TestColumnOrder:
    """Tests for the ColumnOrder dataclass."""

    def test_default_direction(self):
        c = ColumnOrder("name", SQLOrderByDirection.ASC)
        assert c.direction == SQLOrderByDirection.ASC

    def test_descending(self):
        c = ColumnOrder("name", SQLOrderByDirection.DESC)
        assert c.direction == SQLOrderByDirection.DESC


class TestTostr:
    """Tests for Database.tostr static method."""

    def test_none(self):
        assert Database.tostr(None) == "NULL"

    def test_string(self):
        assert Database.tostr("hello") == "'hello'"

    def test_string_with_quote(self):
        assert Database.tostr("it's") == "'it''s'"

    def test_int(self):
        assert Database.tostr(42) == "42"

    def test_float(self):
        assert Database.tostr(3.14) == "3.14"
