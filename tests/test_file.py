"""Tests for pylightlib.io.File."""

import os
import tempfile
import pytest
from pylightlib.io.File import File, FolderItem


class TestExtension:
    """Tests for File.extension."""

    def test_basic_extension(self):
        assert File.extension("readme.txt") == "txt"

    def test_no_extension(self):
        assert File.extension("README") is None

    def test_multiple_dots(self):
        assert File.extension("archive.tar.gz") == "gz"

    def test_hidden_file(self):
        assert File.extension(".gitignore") == "gitignore"

    def test_dot_only(self):
        assert File.extension(".") == ""


class TestChangeExtension:
    """Tests for File.change_extension."""

    def test_basic_change(self):
        assert File.change_extension("file.txt", "md") == "file.md"

    def test_no_extension(self):
        assert File.change_extension("README", "md") == "README"

    def test_multiple_dots(self):
        assert File.change_extension("archive.tar.gz", "xz") == "archive.tar.xz"

    def test_new_extension_empty(self):
        result = File.change_extension("file.txt", "")
        parts = result.split(".")
        assert parts[-1] == ""


class TestPath:
    """Tests for File.path."""

    def test_simple_path(self):
        result = File.path("/foo/bar/file.txt")
        assert result == "/foo/bar"

    def test_root_file(self):
        result = File.path("/file.txt")
        assert result == ""

    def test_deep_path(self):
        result = File.path("/a/b/c/d/file.txt")
        assert result == "/a/b/c/d"

    def test_no_extension(self):
        result = File.path("/foo/bar/README")
        assert result == "/foo/bar"

    def test_trailing_slash_path(self):
        result = File.path("/foo/bar/file.txt")
        assert result == "/foo/bar"


class TestFolderContent:
    """Tests for File.folder_content."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Create some files and subdirectories
            open(os.path.join(tmp, "file1.txt"), "w").close()
            open(os.path.join(tmp, "file2.py"), "w").close()
            os.makedirs(os.path.join(tmp, "subdir"), exist_ok=True)
            open(os.path.join(tmp, "subdir", "file3.txt"), "w").close()
            yield tmp

    def test_list_all(self, temp_dir):
        contents = File.folder_content(temp_dir)
        assert len(contents) >= 2  # file1.txt, file2.py
        # Should return FolderItem objects
        for item in contents.values():
            assert isinstance(item, FolderItem)

    def test_extension_filter(self, temp_dir):
        contents = File.folder_content(temp_dir, extfilter="txt")
        for path, item in contents.items():
            assert item.extension == "txt", f"Item {path} has ext={item.extension}"

    def test_with_subfolders(self, temp_dir):
        contents = File.folder_content(temp_dir, withsubfolders=True)
        # Should find files in subdir too
        paths = list(contents.keys())
        assert any("subdir" in p for p in paths)


class TestCopyFolder:
    """Tests for File.copy_folder."""

    def test_copy_folder_contents(self):
        with tempfile.TemporaryDirectory() as src:
            with tempfile.TemporaryDirectory() as dst:
                # Create a file in src
                open(os.path.join(src, "test.txt"), "w").close()
                File.copy_folder(src, dst)
                # Check file was copied
                assert os.path.exists(os.path.join(dst, "test.txt"))


class TestFolderItem:
    """Tests for the FolderItem dataclass."""

    def test_file_item(self):
        item = FolderItem(type="file", name="test", level=0, extension="txt")
        assert item.type == "file"
        assert item.name == "test"
        assert item.level == 0
        assert item.extension == "txt"

    def test_folder_item(self):
        item = FolderItem(type="folder", name="mydir", level=1)
        assert item.type == "folder"
        assert item.extension is None

    def test_equality(self):
        i1 = FolderItem(type="file", name="a", level=0, extension="txt")
        i2 = FolderItem(type="file", name="a", level=0, extension="txt")
        assert i1 == i2
