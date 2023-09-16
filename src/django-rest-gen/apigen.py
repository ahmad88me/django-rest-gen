import inspect
import sys
import importlib
import os
import django
from django.db import models


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
    """
    Load models from the django project and returns the module object
    :param python_path:
    :param models_fpath:
    :param settings_fpath:
    :return: models.py module object
    """
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

    stops = models_fpath.split(os.sep)
    app_name = stops[-2]
    parts = stops[-1].split(".")
    mod_name = ".".join(parts[:-1])
    mod_pkg_name = f"{app_name}.{mod_name}"
    print(f"loading module: {mod_pkg_name}")

    models_obj = importlib.import_module(mod_pkg_name)
    return models_obj


def write_class_serializer(class_name, fpath):
    content = f"""\nclass {class_name}Serializer(serializers.ModelSerializer):

    class Meta:
        model = {class_name}\n\n"""
    with open(fpath, "a") as f:
        f.write(content)


def write_serializers(classes, serializers_path, app_path):
    exists = False
    if app_path and os.path.exists(app_path):
        with open(serializers_path) as f:
            content = f.read()
            if content.strip() != "":
                exists = True
    if not exists:
        add_serializers_imports(serializers_path=serializers_path, app_path=app_path)
    for class_name in classes:
        write_class_serializer(class_name=class_name, fpath=serializers_path)


def write_class_view(class_name, fpath):
    content = f"""\nclass {class_name}List(generics.ListCreateAPIView):
    queryset = {class_name}.objects.all()
    serializer_class = {class_name}Serializer


class {class_name}Detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = {class_name}.objects.all()
    serializer_class = {class_name}Serializer\n\n"""
    with open(fpath, "a") as f:
        f.write(content)


def add_views_imports(app_path, views_path):
    content = f"""from {app_path}.models import *
from {app_path}.serializers import *
from rest_framework import generics\n\n"""
    with open(views_path, "a") as f:
        f.write(content)


def add_serializers_imports(app_path, serializers_path):
    content = f"""from {app_path}.models import *
from rest_framework import serializers\n\n"""
    with open(serializers_path, "a") as f:
        f.write(content)


def write_views(classes, views_path, app_path):
    """
    Write API views
    :param classes:
    :param views_path:
    :param app_path:

    :return: None
    """
    exists = False
    if app_path and os.path.exists(app_path):
        with open(views_path) as f:
            content = f.read()
            if content.strip() != "":
                exists = True
    if not exists:
        add_views_imports(views_path=views_path, app_path=app_path)
    for class_name in classes:
        write_class_view(class_name=class_name, fpath=views_path)


def workflow(python_path, app_path, settings_fpath):
    models_fpath = os.path.join(app_path, "models.py")
    serializers_path = os.path.join(app_path, "serializers.py")
    views_path = os.path.join(app_path, "views.py")
    models_obj = load_models(python_path=python_path, settings_fpath=settings_fpath, models_fpath=models_fpath)
    classes = get_classes(models_obj)
    write_serializers(classes=classes, serializers_path=serializers_path, app_path=app_path)
    write_views(classes=classes, views_path=views_path, app_path=app_path)
