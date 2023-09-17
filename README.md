# django-rest-gen
This generates a fully functioning apis using generated serializers and class-views. 


# How to use it
1. Install it in your django project `pip install django-rest-gen`.
2. Run it and specify your app `python -m django-rest-gen`. You should also
specify the appropriate arguments (e.g., ` python -m django-rest-gen  --settings iires/settings.py --apppath iirapp`)
*Note: if the file already exists and is not empty, the content will be printed instead in the stdout*

## Arguments
```
usage: django-rest-gen [-h] [--pythonpath PYTHONPATH] --settings SETTINGS --apppath APPPATH [--views VIEWS]

Generate Django REST API code

optional arguments:
  -h, --help            show this help message and exit
  --pythonpath PYTHONPATH
                        Python Path directory.
  --settings SETTINGS   The path to the django project settings
  --apppath APPPATH     The path to the app
  --views VIEWS         The path to the views file
```


# Limitations
* Flat. No nesting is provided as it depends on user preferences.


# Rebuild package
1. `python3 -m build`
2. `python3 -m twine upload dist/*`