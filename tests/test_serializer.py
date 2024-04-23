import pytest
from unittest.mock import mock_open, patch, call
from django_rest_gen.apigen import write_class_serializer, write_serializers


def test_write_class_serializer_prints_correctly():
    class_name = "TestModel"
    fpath = "path/to/your/file.py"

    # Mock print to capture the output
    with patch("builtins.print") as mock_print:
        write_class_serializer(class_name, fpath, write=False)

        expected_output = f"""\nclass {class_name}Serializer(serializers.ModelSerializer):\n
    class Meta:
        model = {class_name}
        fields = '__all__'\n\n"""
        mock_print.assert_called_once_with(expected_output)


def test_write_class_serializer_writes_to_file_correctly():
    class_name = "TestModel"
    fpath = "path/to/your/file.py"
    expected_output = f"""\nclass {class_name}Serializer(serializers.ModelSerializer):\n
    class Meta:
        model = {class_name}
        fields = '__all__'\n\n"""

    # Mock open to avoid actual file operations
    m = mock_open()
    with patch("builtins.open", m):
        write_class_serializer(class_name, fpath, write=True)

        m.assert_called_once_with(fpath, "a")
        handle = m()
        handle.write.assert_called_once_with(expected_output)


@pytest.fixture
def classes():
    return [('Class1',), ('Class2',)]


@pytest.fixture
def serializers_path():
    return 'path/to/serializers.py'


@pytest.fixture
def app_path():
    return 'path/to/app'


# Test the function with typical inputs
def test_write_serializers(classes, serializers_path, app_path):
    with patch('django_rest_gen.utils.empty_fpath') as mock_empty, \
         patch('django_rest_gen.apigen.add_serializers_imports') as mock_add_imports, \
         patch('django_rest_gen.apigen.write_class_serializer') as mock_write_serializer:

        # Setup mock returns
        mock_empty.return_value = True

        # Call the function under test
        write_serializers(classes, serializers_path, app_path)

        # Check if empty_fpath was called correctly
        mock_empty.assert_called_once_with(serializers_path)

        # Check if imports were added correctly
        mock_add_imports.assert_called_once_with(serializers_path=serializers_path, app_path=app_path, write=True)

        # Ensure that write_class_serializer was called for each class
        assert mock_write_serializer.call_count == len(classes)
        calls = [call(class_name=cls[0], fpath=serializers_path, write=True) for cls in classes]
        mock_write_serializer.assert_has_calls(calls, any_order=True)


# Test with no classes
def test_write_serializers_empty(classes, serializers_path, app_path):
    with patch('django_rest_gen.utils.empty_fpath') as mock_empty, \
         patch('django_rest_gen.apigen.add_serializers_imports') as mock_add_imports, \
         patch('django_rest_gen.apigen.write_class_serializer') as mock_write_serializer:

        # Setup the scenario where no classes are provided
        write_serializers([], serializers_path, app_path)

        # Check that class serializer writer was not called
        mock_write_serializer.assert_not_called()
