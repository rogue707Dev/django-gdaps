# this is the API of GDAPS itself.
from gdaps import Interface


class IGdapsPlugin(Interface):
    def plugin_synchronized(self, app):
        """Called when a plugin is synchronized to database"""
