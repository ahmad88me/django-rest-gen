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
    # classes = [(c[0], c[1]._meta.verbose_name_plural.title()) for c in clsmembers if issubclass(c[1], models.Model)]
    classes = [(c[0], c[1]._meta.verbose_name_plural.title(), c[1]._meta.verbose_name.title()) for c in clsmembers if issubclass(c[1], models.Model)]

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
    os.environ["DJANGO_SETTINGS_MODULE"] = proj_settings
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics\n\n"""
    if write:
        with open(views_path, "a") as f:
            f.write(content)
    else:
        print("\n\n\n\n=========================== views.py ===========================\n\n")
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
        print("\n\n\n\n=========================== serializers.py ===========================\n\n")
        print(content)


def write_root_view(views_path, classes, write):
    """
    Write the root api view
    :param views_path:
    :param classes:
    :param write:
    :return:
    """
    lists = ""
    for c in classes:
        name = get_class_url_name(c[2], joiner="-")
        line = f"\t'{name}-list': reverse('{name}-list', request=request, format=format),\n"
        lists += line

    content = f"""@api_view(['GET'])
def api_root(request, format=None):
    return Response({{
{lists}  
    }})
    """

    if write:
        with open(views_path, "a") as f:
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
    write_root_view(views_path=views_path, classes=classes, write=empty)
    for c in classes:
        write_class_view(class_name=c[0], fpath=views_path, write=empty)


def add_urls_imports(app_path, urls_path, write=False):
    """
    Add urls.py required imports
    :param app_path:
    :param urls_path:
    :param write:
    :return:
    """
    content = f"""from {app_path}.models import *
from {app_path} import views
from django.urls import path, re_path, include\n\n"""
    if write:
        with open(urls_path, "a") as f:
            f.write(content)
    else:
        print("\n\n\n\n=========================== urls.py ===========================\n\n")
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
    return url_name


def get_class_url(class_pair):
    """
    Appends the class url path to urls.py
    :param class_pair:
    :return:
    """
    url_name = get_class_url_name(class_pair[2], joiner="-")
    url_name_plural = get_class_url_name(class_pair[1])
    content = f"""\tpath('{url_name_plural}/', views.{class_pair[0]}List.as_view(), name='{url_name}-list'),
\tpath('{url_name_plural}/<int:pk>/', views.{class_pair[0]}Detail.as_view(), name='{url_name}-detail'),\n"""
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

    # root url
    content += "\tpath('', views.api_root)"

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
    if class_pair[0] == "User":
        return ""
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
    content = get_admin_imports(app_path) + content
    if empty:
        with open(admin_path, "a") as f:
            f.write(content)
    else:
        print("\n\n\n\n=========================== admin.py ===========================\n\n")
        print(content)


def write_dummy(classes, app_path, dummy_path, overwrite):
    """

    :param classes:
    :param app_path:
    :param dummy_path:
    :param overwrite:
    :return:
    """
    content = "from model_bakery import baker\nfrom django.contrib.auth.models import User\n\n"
    content += "def run(*args):\n"
    app_name = app_path.split(os.sep)[-1]
    for c in classes:
        if c[0] == "User":
            line = f"\tbaker.make({c[0]})\n"
        else:
            line = f"\tbaker.make('{app_name}.{c[0]}')\n"
        content += line
    empty = utils.empty_fpath(dummy_path)
    if empty or overwrite:
        with open(dummy_path, "w") as f:
            f.write(content)
    else:
        print(content)


def get_curr_path():
    p = os.path.abspath(os.getcwd())
    print(f"current path: {p}")
    return p


def guess_app_path(curr_path=None):
    if not curr_path:
        curr_path = get_curr_path()

    dirs = []
    files = dict()
    for fp in os.listdir(curr_path):
        fp_path = os.path.join(curr_path, fp)
        if os.path.isdir(fp_path):
            dirs.append(fp_path)
        elif os.path.isfile(fp_path):
            files[fp] = fp_path

    if "models.py" in files: # and "views.py" in files:
        with open(files["models.py"]) as f:
            text = f.read()
            if len(text) > 50:
                return curr_path

    for d in dirs:
        guessed = guess_app_path(os.path.join(curr_path, d))
        if guessed:
            return guessed

    return None


def guess_settings_path(curr_path=None):
    if not curr_path:
        curr_path = get_curr_path()

    print(f"DEBUG: curr_path: {curr_path}")
    dirs = []
    for fp in os.listdir(curr_path):
        fp_path = os.path.join(curr_path, fp)
        if os.path.isdir(fp_path):
            print(f"DEBUG is dir: {fp_path}")
            dirs.append(fp_path)
        elif os.path.isfile(fp_path) and fp == "settings.py":
            print(f"DEBUG: found path: {fp_path}")
            return fp_path

    print(f"DEBUG: path not found:")

    for d in dirs:
        print(f"Going into: {d}")
        print(f"should be going to {os.path.join(curr_path, d)}")
        guessed = guess_settings_path(d)
        if guessed:
            return guessed

    return None


def workflow(python_path, app_path, settings_fpath, overwrite, dummy):
    """
    This includes the main workflow of the API generator.
    :param python_path:
    :param app_path:
    :param settings_fpath:
    :param overwrite: bool
    :param dummy: bool
    :return:
    """
    if not app_path:
        app_path = guess_app_path()
        if app_path is None:
            raise Exception("Unable to detect app path.")
        else:
            print(f"Guessed app path: {app_path}")

    if not settings_fpath:
        settings_fpath = guess_settings_path()
        if settings_fpath is None:
            raise Exception("Unable to detect settings path")
        else:
            print(f"Guessed settings path: {settings_fpath}")

    models_fpath = os.path.join(app_path, "models.py")
    serializers_path = os.path.join(app_path, "serializers.py")
    views_path = os.path.join(app_path, "views.py")
    urls_path = os.path.join(app_path, "urls.py")
    admin_path = os.path.join(app_path, "admin.py")
    dummy_path = os.path.join(app_path, "dummygen.py")
    if overwrite:
        for fpath in [serializers_path, views_path, urls_path, admin_path]:
            with open(fpath, 'w') as f:
                f.write('')
    models_obj = load_models(python_path=python_path, settings_fpath=settings_fpath, models_fpath=models_fpath)
    classes = get_classes(models_obj)
    write_serializers(classes=classes, serializers_path=serializers_path, app_path=app_path)
    write_views(classes=classes, views_path=views_path, app_path=app_path)
    write_urls(classes=classes, app_path=app_path, urls_path=urls_path)
    write_admin(classes=classes, app_path=app_path, admin_path=admin_path)
    if dummy:
        write_dummy(classes, app_path, dummy_path, overwrite)