import pytest
from unittest.mock import mock_open, patch, call
from django_rest_gen.apigen import write_class_view, write_views, add_views_imports, get_app_name


def test_write_class_view_prints_correctly():
    class_name = "TestModel"
    fpath = "path/to/your/file.py"

    # Mock print to capture the output
    with patch("builtins.print") as mock_print:
        write_class_view(class_name, fpath, write=False)

        expected_output = f"""\nclass {class_name}List(generics.ListCreateAPIView):
    queryset = {class_name}.objects.all()
    serializer_class = {class_name}Serializer\n\n
class {class_name}Detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = {class_name}.objects.all()
    serializer_class = {class_name}Serializer\n\n"""

        mock_print.assert_called_once_with(expected_output)


def test_write_class_view_writes_to_file_correctly():
    class_name = "TestModel"
    fpath = "path/to/your/file.py"
    expected_output = (
        "\nclass TestModelList(generics.ListCreateAPIView):\n"
        "    queryset = TestModel.objects.all()\n"
        "    serializer_class = TestModelSerializer\n\n"
        "class TestModelDetail(generics.RetrieveUpdateDestroyAPIView):\n"
        "    queryset = TestModel.objects.all()\n"
        "    serializer_class = TestModelSerializer\n\n"
    )

    expected_output = expected_output.replace("\n", "").replace("\t", "").strip()
    print("\n\n\nExpected Output:")
    print(expected_output)
    # Mock open to avoid actual file operations
    m = mock_open()
    with patch("builtins.open", m):
        write_class_view(class_name, fpath, write=True)

        # Assert that open was called correctly
        m.assert_called_once_with(fpath, "a")
        handle = m()

        # Check what was actually written to the file
        actual_written_output = "".join(call.args[0] for call in handle.write.call_args_list)
        actual_written_output = actual_written_output.replace("\n", "").replace("\t", "").strip()
        print("\n\n\nActual Output Written:")
        print(actual_written_output)

        assert actual_written_output == expected_output


@pytest.fixture
def classes():
    return [('Class1', 'Class1', 'Class1'), ('Class2', 'Class2', 'Class2')]


@pytest.fixture
def views_path():
    return 'path/to/views.py'


@pytest.fixture
def app_path():
    return 'path/to/app'


# Test the function with typical inputs
def test_write_views(classes, views_path, app_path):
    with (patch('django_rest_gen.utils.empty_fpath') as mock_empty,
          patch('django_rest_gen.apigen.write_root_view') as mock_write_root_view,
          patch('django_rest_gen.apigen.add_views_imports') as mock_add_imports,
          patch('django_rest_gen.apigen.write_class_view') as mock_write_view):

        # Setup mock returns
        mock_empty.return_value = True

        # Call the function under test
        write_views(classes, views_path, app_path)

        # Check if empty_fpath was called correctly
        mock_empty.assert_called_once_with(fpath=views_path)

        # Check if imports were added correctly
        # mock_add_imports.assert_called_once_with(views_path=views_path, app_path=app_path, write=True)
        mock_add_imports.assert_called_once_with(views_path=views_path, app_name=get_app_name(app_path), write=True)

        assert mock_write_view.call_count == len(classes)
        calls = [call(class_name=cls[0], fpath=views_path, write=True) for cls in classes]
        mock_write_view.assert_has_calls(calls, any_order=True)


# Test with no classes
def test_write_view_empty(classes, views_path, app_path):
    with patch('django_rest_gen.utils.empty_fpath') as mock_empty, \
            patch('django_rest_gen.apigen.add_views_imports') as mock_add_imports, \
            patch('django_rest_gen.apigen.write_class_view') as mock_write_view:
        mock_empty.return_value = False

        # Setup the scenario where no classes are provided
        write_views([], views_path, app_path)

        mock_write_view.assert_not_called()


# Test the function with typical inputs
def test_add_views_imports_without_writing(monkeypatch, capfd):
    with patch('django_rest_gen.utils.empty_fpath') as mock_empty, \
            patch('django_rest_gen.apigen.write_class_view') as mock_write_view:
        # Setup mock returns
        mock_empty.return_value = False

        m = mock_open()
        monkeypatch.setattr("builtins.open", m)

        app_path = "/path/to/my_app"
        views_path = "/path/to/my_app/views.py"

        # Call the function under test
        write_views([], views_path, app_path)

        out, err = capfd.readouterr()

        mock_empty.assert_called_once_with(fpath=views_path)

        assert "from my_app.models import *" in out
        assert "from my_app.serializers import *" in out


def test_add_views_imports_with_writing(monkeypatch):
    with patch('django_rest_gen.utils.empty_fpath') as mock_empty, \
            patch('django_rest_gen.apigen.write_root_view') as mock_root, \
            patch('django_rest_gen.apigen.write_class_view') as mock_write_view:
        app_path = "/path/to/my_app"
        views_path = "/path/to/my_app/views.py"

        # Setup a mock for the open function
        m = mock_open(read_data="Existing content")
        monkeypatch.setattr("builtins.open", m)

        # Call the function with `write` set to True
        write_views([], views_path, app_path)

        # Check if open was called correctly
        m.assert_called_with(views_path, "a")  # If open could be called multiple times, use assert_called_with

        # Get the mock file handle
        handle = m()
        expected_output = (
            "from my_app.models import *\n"
            "from my_app.serializers import *\n"
            "from rest_framework.decorators import api_view\n"
            "from rest_framework.response import Response\n"
            "from rest_framework.reverse import reverse\n"
            "from rest_framework import generics\n\n"
        )
        # Check the actual arguments passed to handle.write()
        actual_write_calls = handle.write.call_args_list
        assert actual_write_calls == [call(expected_output)]

        # Optionally, check for the number of write operations
        assert handle.write.call_count == 1
