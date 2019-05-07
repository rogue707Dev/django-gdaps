"""
Settings for GDAPS are all namespaced in the GDAPS setting.
For example your project's `settings.py` file might look like this:
GDAPS = {
    "FRONTEND_DIR": "frontend"
    )
}
This module provides the `gdaps_settings` object, that is used to access
GDAPS settings, checking for user settings first, then falling
back to the defaults.
"""
import os
from importlib import import_module

from django.conf import settings
from django.test.signals import setting_changed

# Copied shamelessly from Graphene-Django, with little adaptions

NAMESPACE = "GDAPS"


DEFAULTS = {"FRONTEND_DIR": "frontend"}

# List of settings that may be in string import notation.
IMPORT_STRINGS = []

# List of settings that have been removed
REMOVED_SETTINGS = ()


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
        parts = val.split(".")
        module_path, class_name = ".".join(parts[:-1]), parts[-1]
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
        from gdaps.conf import gdaps_settings
        print(gdaps_settings.FRONTEND_DIR)
    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(
        self,
        namespace: str = None,
        user_settings: list = None,
        defaults: list = None,
        import_strings=None,
        removed_settings=None,
    ):

        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self.removed_settings = removed_settings or REMOVED_SETTINGS

        if not namespace == namespace.upper():
            raise RuntimeError("Django settings must be UPPERCASE.")
        self._namespace = namespace or NAMESPACE

        setting_changed.connect(self.reload)

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, self._namespace, {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr in self.removed_settings:
            raise AttributeError(
                "Invalid access - Plugin settings attribute '%s' has invalid (removed) key: '%s'."
                % (self._namespace, attr)
            )
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

        setattr(self, attr, val)
        return val

    @staticmethod
    def reload(*args, **kwargs):
        global gdaps_settings
        setting, value = kwargs["setting"], kwargs["value"]
        if setting == NAMESPACE:
            gdaps_settings = PluginSettings(NAMESPACE, value, DEFAULTS, IMPORT_STRINGS)


gdaps_settings = PluginSettings(NAMESPACE, None, DEFAULTS, IMPORT_STRINGS)
