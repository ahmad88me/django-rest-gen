import inspect
import sys
import importlib
import os
from importlib import import_module
import django
from django.db import models

#
# def get_classes(fpath):
#     """
#     Get class names from models.py file
#
#     :param fpath: the path of the models.py file
#     :return: list of classes
#     """
#     stops = fpath.split(os.sep)
#     ppath = os.sep.join(stops[:-1])
#     sys.path = [ppath] + sys.path
#     parts = stops[-1].split(".")
#     mod_name = ".".join(parts[:-1])
#     importlib.import_module(mod_name)
#     print(sys.modules)
#     classes = []
#     # clsmembers = inspect.getmembers(sys.modules[fpath], inspect.isclass)
#     # return clsmembers
#     return classes


def get_classes(models_obj):
    """
    Get class names from models.py file

    :param fpath: the path of the models.py file
    :return: list of classes
    """
    # Get classes
    clsmembers = inspect.getmembers(models_obj, inspect.isclass)

    # Filter Models
    class_names = [c[0] for c in clsmembers if issubclass(c[1], models.Model)]
    print(f"classes: {class_names}")
    return class_names


def load_models(python_path, models_fpath, settings_fpath):

    # Add path
    sys.path = [python_path] + sys.path

    # Setup Django
    settings_stops = settings_fpath.split(os.sep)
    proj_settings = ".".join(settings_stops[-2:])
    if proj_settings[-3:] == ".py":
        proj_settings = proj_settings[:-3]

    print(f"Project settings {proj_settings}")
    os.environ["DJANGO_SETTINGS_MODULE"] = proj_settings #"iires.settings"
    django.setup()

    # Load models module
    #
    # # Import the inspect module
    # import inspect
    # stops = models_fpath.split(os.sep)
    # ppath = os.sep.join(stops[:-1])
    # sys.path = [ppath] + sys.path
    # for fp in sys.path:
    #     print(fp)

    stops = models_fpath.split(os.sep)
    app_name = stops[-2]
    parts = stops[-1].split(".")
    mod_name = ".".join(parts[:-1])
    mod_pkg_name = f"{app_name}.{mod_name}"
    print(f"loading module: {mod_pkg_name}")

    models_obj = importlib.import_module(mod_pkg_name)
    return models_obj
    # importlib.import_module(mod_name)
    # Import the models module from the django project
    # Get a list of all classes defined in the models module
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


def workflow(python_path, models_fpath, settings_fpath, views_path, serializers_path):
    models_obj = load_models(python_path=python_path, settings_fpath=settings_fpath, models_fpath=models_fpath)
    classes = get_classes(models_obj)
    print(f"classes: {classes}")
#
# print(f"stack: {inspect.stack()}")
#
# ppath  = "/Users/aalobaid/Workspaces/Pyspace/iirestaurant-api/iirapp"
# sys.path = [ppath] + sys.path
#
# import os, sys, django
# os.environ["DJANGO_SETTINGS_MODULE"] = "iires.settings"
# sys.path.insert(0, os.getcwd())
#
# django.setup()
#
# itertools = importlib.import_module("iirapp.models")
#



# fpath = "/Users/aalobaid/Workspaces/Pyspace/iirestaurant-api/iirapp/models.py"
# # classes = get_classes(fpath)
# classes = get_classes2(fpath)
# print(f"get classes: {classes}")


# module = imp.new_module(name)
#
#     if add_to_sys_modules:
#         import sys
#         sys.modules[name] = module
#     exec code in module._ _dict_ _
