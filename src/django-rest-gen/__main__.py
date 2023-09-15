
import argparse
import os
import sys
# base_path = os.path.abspath('.')
# print(f"abs path {base_path}")
# print(sys.argv)
from . import apigen


def main():
    parser = argparse.ArgumentParser(prog='django-rest-gen', description='Generate Django REST API code')
    parser.add_argument('--pythonpath', default=".", help="Python Path directory. ")
    parser.add_argument('--settings', required=True, help="The path to the django project settings")
    parser.add_argument('--models', required=True, help="The path to the models.py file")
    parser.add_argument('--serializers', default=None, help="The path to the serializers file")
    parser.add_argument('--views', default=None, help="The path to the views file")
    args = parser.parse_args()
    print(f"args: {args}")
    base_path = os.path.abspath('.')
    apigen.workflow(python_path=base_path, settings_fpath=args.settings, models_fpath=args.models,
                    serializers_path=args.serializers, views_path=args.views)

#
# sys.path.append('/path/to/myproject')
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.file")
# import django
# django.setup()


main()
# from .apigen import *


# # Import the inspect module
# import inspect
#
# # Import the models module from the django project
# from my_project import models
#
# # Get a list of all classes defined in the models module
# classes = inspect.getmembers(models, inspect.isclass)
#
# # Filter out the classes that do not inherit from django.db.models.Model
# classes = [c for c in classes if issubclass(c[1], models.Model)]
#
# # Print the names and definitions of the classes
# for name, cls in classes:
#     print(name)
#     print(inspect.getsource(cls))
#     print()