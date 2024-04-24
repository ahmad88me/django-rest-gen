import pytest
from unittest.mock import patch, mock_open, MagicMock
import django_rest_gen
from django_rest_gen.apigen import write_urls


@pytest.fixture
def mock_dependencies(monkeypatch):
    # Mock external utilities and file opening
    monkeypatch.setattr("django_rest_gen.utils.empty_fpath", MagicMock())
    monkeypatch.setattr("django_rest_gen.apigen.add_urls_imports", MagicMock())
    monkeypatch.setattr("django_rest_gen.apigen.get_class_url", MagicMock(return_value="path('url/', views.view_name),\n"))
    monkeypatch.setattr("builtins.open", mock_open())


def test_write_urls_empty_true(mock_dependencies):
    classes = [('ModelName', 'Model')]
    app_path = "/path/to/app"
    urls_path = "/path/to/app/urls.py"

    with patch('builtins.open', mock_open()) as mocked_file:
        django_rest_gen.utils.empty_fpath.return_value = True
        write_urls(classes, app_path, urls_path)

        # Ensure the file is opened correctly for appending
        mocked_file.assert_called_once_with(urls_path, "a")
        handle = mocked_file()

        # Verify content written to the file
        expected_content = (
            "urlpatterns = [\n"
            "path('url/', views.view_name),\n"
            "\tpath('', views.api_root)\n"
            "]"
        )
        handle.write.assert_called_once_with(expected_content)


def test_write_urls_empty_false(mock_dependencies, capsys):
    classes = [('ModelName', 'Model')]
    app_path = "/path/to/app"
    urls_path = "/path/to/app/urls.py"

    django_rest_gen.utils.empty_fpath.return_value = False
    write_urls(classes, app_path, urls_path)

    # Capture the printed output
    captured = capsys.readouterr()
    expected_content = (
        "urlpatterns = [\n"
        "path('url/', views.view_name),\n"
        "\tpath('', views.api_root)\n"
        "]\n"
    )
    assert expected_content in captured.out
    # assert captured.out == expected_content












# Test the function with typical inputs
def test_urls_imports_without_writing(monkeypatch, capfd):
    with patch('django_rest_gen.utils.empty_fpath') as mock_empty:

        # Setup mock returns
        mock_empty.return_value = False

        m = mock_open()
        monkeypatch.setattr("builtins.open", m)

        app_path = "/path/to/myapp"
        urls_path = "/path/to/myapp/urls.py"

        # Call the function under test
        write_urls([], urls_path=urls_path, app_path=app_path)

        out, err = capfd.readouterr()

        print(f"\n\nThe OUT was being debugged: {out}\n\n")

        # Check if empty_fpath was called correctly
        mock_empty.assert_called_once_with(fpath=urls_path)

        assert "from myapp.models import *" in out
        assert "from myapp import views" in out