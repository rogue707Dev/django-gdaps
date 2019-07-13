import os

SECRET_KEY = "test"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.admin",
    "gdaps",
    "tests.plugins.plugin1.apps.Plugin1Config",
]

PLUGIN1 = {"OVERRIDE": 20}
