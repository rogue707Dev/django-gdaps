__all__ = ["PluginError", "IncompatibleVersionsError"]


class PluginError(Exception):
    """An Exception that marks an error in a plugin specific setting."""


class IncompatibleVersionsError(PluginError):
    """Exception that occurs when plugins that are not compatible are installed together."""
