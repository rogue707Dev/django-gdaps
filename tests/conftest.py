import os

from django.conf import settings


def pytest_configure():
    settings.configure(
        BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.admin",
            "gdaps",
            "gdaps.test.plugins.plugin1",
        ],
        # plugin1 specific settings
        PLUGIN1={"OVERRIDE": 20},
    )
