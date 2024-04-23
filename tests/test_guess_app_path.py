import os
import pytest
from unittest.mock import Mock, mock_open
from django_rest_gen.apigen import guess_app_path


def mock_get_curr_path():
    return "/fake/app_directory"


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
    # Mock opening files to read data
    m = mock_open(read_data="Some content longer than 50 characters to simulate valid models.py content.")
    monkeypatch.setattr("builtins.open", m)
    # Mock get_curr_path to return a fixed directory path
    monkeypatch.setattr('django_rest_gen.apigen.get_curr_path', mock_get_curr_path)


def test_app_path_with_valid_models_in_current_directory(mock_filesystem):
    os.listdir.return_value = ["models.py", "views.py"]
    os.path.isdir.return_value = False
    os.path.isfile.side_effect = lambda x: x.endswith(".py")

    result = guess_app_path()
    assert result == "/fake/app_directory"


def test_app_path_with_valid_models_in_subdirectory(mock_filesystem):
    os.listdir.side_effect = [["dir1"], ["models.py"]]
    os.path.isdir.side_effect = lambda x: "dir" in x.split("/")[-1]
    os.path.isfile.side_effect = lambda x: x.endswith(".py")

    result = guess_app_path()
    assert result == "/fake/app_directory/dir1"


def test_models_file_too_short(mock_filesystem, monkeypatch):
    os.listdir.return_value = ["models.py"]
    os.path.isdir.return_value = False
    os.path.isfile.return_value = True
    # Override the mock to have less than 50 characters
    monkeypatch.setattr("builtins.open", mock_open(read_data="Short content"))

    result = guess_app_path()
    assert result is None