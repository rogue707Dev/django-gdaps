import os

SECRET_KEY = "test"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
INSTALLED_APPS = ["gdaps", "tests.plugins.plugin1.apps.Plugin1Config"]

PLUGIN1 = {"OVERRIDE": 20}
