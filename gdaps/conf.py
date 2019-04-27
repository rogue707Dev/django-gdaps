import os
from importlib import import_module

from django.conf import settings
from django.test.signals import setting_changed


NAMESPACE = "GDAPS"

DEFAULTS = {
    "PLUGIN_PATH": "plugins",
    "FRONTEND_PATH": os.path.join(settings.BASE_DIR, "frontend"),
    "FRONTEND_DIR": "frontend",
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = ()

# List of settings that have been removed
REMOVED_SETTINGS = ()


# Shamelessly copied from Django Rest Framework...


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        module_path, class_name = val.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = "Could not import '%s' for plugin setting '%s'. %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


class PluginSettings:
    """
    A settings object, that allows app specific settings to be accessed as properties.
    For example:
        from my_app.conf import settings
        print(settings.MY_SETTING)
    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(
        self,
        namespace: str,
        defaults: list or tuple = None,
        import_strings: list or tuple = None,
        removed_settings: list or tuple = None,
        help_url: str = None,
    ):
        """

        :param namespace: settings namespace that should be used by this plugin
        :param help_url: An optional URL where to find information in the internet about these settings
        :param defaults: a dict of settings that are used as fallback when there are no user settings
        """
        if not namespace == namespace.upper():
            raise RuntimeError("Django settings must be UPPERCASE.")

        self._namespace = namespace

        self._removed_settings = removed_settings or REMOVED_SETTINGS
        self._user_settings = self.__check_user_settings(
            getattr(settings, self._namespace, {})
        )
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

        self._url = help_url

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, self._namespace, {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(
                "Invalid access - Plugin settings attribute '%s' has missing key: '%s'"
                % (self._namespace, attr)
            )

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        for setting in self._removed_settings:
            if setting in user_settings:
                msg = "The '%s' setting has been removed." % setting
                if self._url:
                    msg += " Please refer to '%s' for available settings." % self._url
                raise RuntimeError(msg)
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


gdaps_settings = PluginSettings(NAMESPACE, DEFAULTS, IMPORT_STRINGS)


def reload_gdaps_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == NAMESPACE:
        gdaps_settings.reload()


setting_changed.connect(reload_gdaps_settings)

assert gdaps_settings.PLUGIN_PATH
