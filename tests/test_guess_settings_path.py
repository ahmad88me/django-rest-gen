import os
import pytest
from unittest.mock import Mock
from django_rest_gen.apigen import guess_settings_path  # Adjust the import according to your package structure


# Mock the get_curr_path function if it's not directly related to filesystem functions
def mock_get_curr_path():
    return "/fake/directory"


@pytest.fixture
def mock_filesystem(monkeypatch):
    # Mock os.listdir to control directory listing
    monkeypatch.setattr(os, 'listdir', Mock())
    # Mock os.path.join to behave normally
    monkeypatch.setattr(os.path, 'join', os.path.join)
    # Mock os.path.isdir to identify directories
    monkeypatch.setattr(os.path, 'isdir', Mock())
    # Mock os.path.isfile to identify files
    monkeypatch.setattr(os.path, 'isfile', Mock())
    # Mock get_curr_path to return a fixed directory path
    monkeypatch.setattr('django_rest_gen.apigen.get_curr_path', mock_get_curr_path)


def test_no_settings_file_found(mock_filesystem):
    os.listdir.return_value = [ "file1.txt", "file2.log"]
    os.path.isdir.side_effect = lambda x: "dir" in x.split("/")[-1]
    os.path.isfile.return_value = False

    result = guess_settings_path()
    assert result is None


def test_settings_file_in_current_directory(mock_filesystem):
    os.listdir.return_value = ["settings.py", "file1.txt"]
    os.path.isdir.return_value = False
    os.path.isfile.side_effect = lambda x: x.endswith("settings.py")

    result = guess_settings_path()
    assert result == "/fake/directory/settings.py"


def test_settings_file_in_subdirectory(mock_filesystem):
    os.listdir.side_effect = [["dir1"], ["settings.py"]]
    os.path.isdir.side_effect = lambda x: "dir" in x.split("/")[-1]
    # os.path.isdir.side_effect = lambda x: "dir" in x
    os.path.isfile.side_effect = lambda x: x.endswith("settings.py")

    result = guess_settings_path()
    assert result == "/fake/directory/dir1/settings.py"
