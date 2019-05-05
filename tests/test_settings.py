import pytest

from gdaps import InterfaceMeta
from gdaps.conf import PluginSettings
from .plugins.plugin1.conf import plugin1_settings, NAMESPACE, IMPORT_STRINGS
from .plugins.plugin1.api.interfaces import FirstInterface


def test_simple_default_value():
    """Tests a simple settings default value"""
    assert plugin1_settings.FOO == 33


def test_override_settings():
    """Tests user overriding a default setting"""
    # default = 10, override = 20
    assert plugin1_settings.OVERRIDE == 20


def test_correct_arrayimport():
    """Tests a settings default array value"""
    assert plugin1_settings.ARRAY == [1, 2, 3]


def test_correct_stringimport():
    """Tests a settings string import functionality"""

    assert type(plugin1_settings.INTERFACE) is InterfaceMeta
    assert plugin1_settings.INTERFACE is FirstInterface


def test_notallowed_stringimport():
    defaults = {"FOO": "tests.plugins.plugin1.api.interfaces.FirstInterface"}
    settings = PluginSettings(
        namespace=NAMESPACE, defaults=defaults, import_strings=IMPORT_STRINGS
    )

    assert type(settings.FOO) is str
    assert settings.FOO == "tests.plugins.plugin1.api.interfaces.FirstInterface"


def test_notexisting_stringimport():
    defaults = {"FOO": "tests.plugins.plugin1.Blah"}
    settings = PluginSettings(
        namespace=NAMESPACE, defaults=defaults, import_strings=("FOO")
    )

    with pytest.raises(ImportError):
        foo = settings.FOO


def test_notexisting_setting_access():
    defaults = {"FOO": 234}
    settings = PluginSettings(
        namespace=NAMESPACE, defaults=defaults, import_strings=IMPORT_STRINGS
    )

    with pytest.raises(AttributeError):
        settings.BLAHFOO


def test_notallowed_removed_setting_access():
    defaults = {"FOO": 234}
    removed_settings = "BAR"
    settings = PluginSettings(
        namespace=NAMESPACE,
        defaults=defaults,
        import_strings=IMPORT_STRINGS,
        removed_settings=removed_settings,
    )

    with pytest.raises(AttributeError):
        settings.BAR
