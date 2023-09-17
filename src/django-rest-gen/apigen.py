import inspect
import sys
import importlib
import os
from . import utils
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
    classes = [(c[0], c[1]._meta.verbose_name_plural.title()) for c in clsmembers if issubclass(c[1], models.Model)]
    print(f"classes: {classes}")
    return classes


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


def write_class_serializer(class_name, fpath, write=False):
    """
    Write a serializer for the given class
    :param class_name:
    :param fpath:
    :param write:
    :return:
    """
    content = f"""\nclass {class_name}Serializer(serializers.ModelSerializer):\n
    class Meta:
        model = {class_name}
        fields = '__all__'\n\n"""
    if write:
        with open(fpath, "a") as f:
            f.write(content)
    else:
        print(content)


def write_serializers(classes, serializers_path, app_path):
    """
    Write serializers for all provided classes
    :param classes:
    :param serializers_path:
    :param app_path:
    :return:
    """
    empty = utils.empty_fpath(serializers_path)
    add_serializers_imports(serializers_path=serializers_path, app_path=app_path, write=empty)
    for c in classes:
        write_class_serializer(class_name=c[0], fpath=serializers_path, write=empty)


def write_class_view(class_name, fpath, write=False):
    """
    Write the view for a single class
    :param class_name:
    :param fpath:
    :param write:
    :return:
    """
    content = f"""\nclass {class_name}List(generics.ListCreateAPIView):
    queryset = {class_name}.objects.all()
    serializer_class = {class_name}Serializer\n\n
class {class_name}Detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = {class_name}.objects.all()
    serializer_class = {class_name}Serializer\n\n"""
    if write:
        with open(fpath, "a") as f:
            f.write(content)
    else:
        print(content)


def add_views_imports(app_path, views_path, write=False):
    """
    Add the imports for views.py
    :param app_path:
    :param views_path:
    :param write:
    :return:
    """
    content = f"""from {app_path}.models import *
from {app_path}.serializers import *
from rest_framework import generics\n\n"""
    if write:
        with open(views_path, "a") as f:
            f.write(content)
    else:
        print(content)


def add_serializers_imports(app_path, serializers_path, write=False):
    """
    Add the imports for serializers.py
    :param app_path:
    :param serializers_path:
    :param write:
    :return:
    """
    content = f"""from {app_path}.models import *
from rest_framework import serializers\n\n"""
    if write:
        with open(serializers_path, "a") as f:
            f.write(content)
    else:
        print(content)


def write_views(classes, views_path, app_path):
    """
    Write API views
    :param classes:
    :param views_path:
    :param app_path:

    :return: None
    """
    empty = utils.empty_fpath(fpath=views_path)
    add_views_imports(views_path=views_path, app_path=app_path, write=empty)
    for c in classes:
        write_class_view(class_name=c[0], fpath=views_path, write=empty)


def add_urls_imports(app_path, urls_path, write=False):
    content = f"""from {app_path}.models import *
from {app_path} import views
from django.urls import path, re_path, include\n\n"""
    if write:
        with open(urls_path, "a") as f:
            f.write(content)
    else:
        print(content)


def get_class_url_name(verbose_name, joiner="_"):
    """
    Transform the class verbose name to a url friendly name
    :param verbose_name:
    :param joiner:
    :return:
    """
    url_name = verbose_name.replace(" ", joiner)
    url_name = url_name.lower()
    # print(f" {verbose_name} -> {url_name}")
    return url_name


def get_class_url(class_pair):
    """
    Appends the class url path to urls.py
    :param class_pair:
    :return:
    """
    url_name = get_class_url_name(class_pair[1])
    content = f"""\tpath('{url_name}/', views.{class_pair[0]}List.as_view()),
\tpath('{url_name}/<int:pk>/', views.{class_pair[0]}Detail.as_view()),\n"""
    return content


def write_urls(classes, app_path, urls_path):
    """
    Generates the code for the urls.py
    :param classes:
    :param app_path:
    :param urls_path:
    :return:
    """
    empty = utils.empty_fpath(urls_path)
    add_urls_imports(urls_path=urls_path, app_path=app_path, write=empty)

    content = ""

    for c in classes:
        content += get_class_url(class_pair=c)

    content = f"urlpatterns = [\n{content}\n]"

    if empty:
        with open(urls_path, "a") as f:
            f.write(content)

    else:
        print(content)


def get_class_admin(class_pair):
    """
    Code to add a single class to admin page
    :param class_pair:
    :return:
    """
    content = f"admin.site.register({class_pair[0]})\n"
    return content


def get_admin_imports(app_path):
    """
    Generate admin imports
    :param app_path:
    :return:
    """
    app_name = app_path.split(os.sep)[-1]
    content = f"from django.contrib import admin\nfrom {app_name}.models import *\n\n"
    return content


def write_admin(classes, app_path, admin_path):
    """
    Writes the admin.py from the given classes
    :param classes:
    :param app_path:
    :param admin_path:
    :return:
    """
    content = ""
    for c in classes:
        content += get_class_admin(c)
    empty = utils.empty_fpath(admin_path)
    if empty:
        with open(admin_path, "a") as f:
            content = get_admin_imports(app_path) + content
            f.write(content)
    else:
        print(content)


def workflow(python_path, app_path, settings_fpath):
    """
    This includes the main workflow of the API generator.
    :param python_path:
    :param app_path:
    :param settings_fpath:
    :return:
    """
    models_fpath = os.path.join(app_path, "models.py")
    serializers_path = os.path.join(app_path, "serializers.py")
    views_path = os.path.join(app_path, "views.py")
    urls_path = os.path.join(app_path, "urls.py")
    admin_path = os.path.join(app_path, "admin.py")
    models_obj = load_models(python_path=python_path, settings_fpath=settings_fpath, models_fpath=models_fpath)
    classes = get_classes(models_obj)
    write_serializers(classes=classes, serializers_path=serializers_path, app_path=app_path)
    write_views(classes=classes, views_path=views_path, app_path=app_path)
    write_urls(classes=classes, app_path=app_path, urls_path=urls_path)
    write_admin(classes=classes, app_path=app_path, admin_path=admin_path)