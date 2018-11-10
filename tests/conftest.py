from django.conf import settings

def pytest_configure():
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.admin",
            'gdaps',
            'gdaps.test.plugins.plugin1'
        ],
    )
