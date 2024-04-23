# django-rest-gen
![tests](https://github.com/ahmad88me/django-rest-gen/actions/workflows/pytest.yml/badge.svg)

This generates a fully functioning apis using generated serializers and class-views. 


# How to use it
1. Install it in your django project `pip install django-rest-gen`.
2. Run it and specify your app `python -m django_rest_gen`. You should also
specify the appropriate arguments (e.g., `python -m django_rest_gen  --settings iires/settings.py --apppath iirapp`)
*Note: if the file already exists and is not empty, the content will be printed instead in the stdout*

## Arguments
``` 
usage: django_rest_gen [-h] [--pythonpath PYTHONPATH] [--settings SETTINGS] [--apppath APPPATH] [--overwrite] [--dummy]

Generate Django REST API code

options:
  -h, --help            show this help message and exit
  --pythonpath PYTHONPATH
                        Python Path directory.
  --settings SETTINGS   The path to the django project settings
  --apppath APPPATH     The path to the app
  --overwrite           Whether to overwrite existing files if any
  --dummy               Whether to generate dummy data generator

```

## Automatic detection
If `--settings` and `--apppath` are not passed, it will try to detect them. It will look for anypath
within your project that has `settings.py` to be the default settings path and any directory that has
`models.py` to be the app path. You need to specify this in case you have multiple apps in your django 
project.


# Limitations
* Flat. No nesting is provided as it depends on user preferences.


# Rebuild package
1. `python3 -m build`
2. `python3 -m twine upload dist/*`