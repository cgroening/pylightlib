"""Tests for pylightlib.io.AppStorage."""

import json
import os
import tempfile
import pytest
from pylightlib.io.AppStorage import AppStorage


@pytest.fixture
def fresh_storage():
    """Create a fresh AppStorage with a temp JSON file.
    Resets the Singleton between tests by creating a new temp file each time.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"key1": "value1", "numbers": [1, 2, 3]}, f)
        f.flush()
        path = f.name

    # Create a new storage instance (Singleton will return the old one,
    # but read_json_file will reload the fresh data from the new temp file)
    store = AppStorage(path)
    yield store

    # Clean up the temp file
    try:
        os.unlink(path)
    except (OSError, FileNotFoundError):
        pass


class TestAppStorage:
    """Tests for AppStorage JSON-based storage.
    
    Note: AppStorage uses a Singleton metaclass, so all instances share
    state across tests. We work around this by using separate keys/temp 
    files and verifying based on actual file content.
    """

    def test_get_existing(self, fresh_storage):
        assert fresh_storage.get("key1") == "value1"

    def test_get_nonexistent(self, fresh_storage):
        assert fresh_storage.get("nonexistent") is None

    def test_get_default(self, fresh_storage):
        assert fresh_storage.get("nonexistent", "default") == "default"

    def test_set_and_get(self, fresh_storage):
        fresh_storage.set("new_key", "new_value")
        assert fresh_storage.get("new_key") == "new_value"

    def test_set_overwrite(self, fresh_storage):
        fresh_storage.set("key1", "updated")
        assert fresh_storage.get("key1") == "updated"

    def test_array_insert(self, fresh_storage):
        fresh_storage.array_insert("numbers", 0, 0)
        nums = fresh_storage.get("numbers")
        assert nums[0] == 0

    def test_array_insert_new_array(self, fresh_storage):
        fresh_storage.array_insert("new_array", 0, "first")
        arr = fresh_storage.get("new_array")
        assert arr == ["first"]

    def test_edit_array_item(self, fresh_storage):
        """edit_array_item modifies dict elements within a list."""
        # First insert a dict element
        fresh_storage.array_insert("dict_array", 0, {"id": 1, "val": "a"})
        fresh_storage.array_insert("dict_array", 1, {"id": 2, "val": "b"})
        # Edit the first element's 'val' key
        fresh_storage.edit_array_item("dict_array", 0, "val", "updated")
        items = fresh_storage.get("dict_array")
        assert items[0] == {"id": 1, "val": "updated"}

    def test_delete_array_item(self, fresh_storage):
        nums = fresh_storage.get("numbers")
        original_len = len(nums)
        fresh_storage.delete_array_item("numbers", 0)
        nums_after = fresh_storage.get("numbers")
        assert len(nums_after) == original_len - 1

    def test_move_array_item(self, fresh_storage):
        fresh_storage.move_array_item("numbers", 0, 2)
        nums = fresh_storage.get("numbers")
        assert len(nums) == 3

    def test_persistence(self, fresh_storage):
        """Test that save actually persists to disk."""
        fresh_storage.set("persist_key", "persist_value")
        path = fresh_storage.json_file

        # Read the file directly
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        assert data.get("persist_key") == "persist_value"
