from typing import List

from gdaps import Interface


class IFrontendEngine(Interface):
    class Meta:
        service = False

    name = None
    files = []

    @staticmethod
    def initialize():
        """Initializes engine.

        This method is called when the frontend is created, and will be only called once.
        It should install all frontend specific stuff, e.g. using Js libraries using 'npm install' etc.
        """

    @staticmethod
    def update_plugins_list(plugins_list: List[str]) -> None:
        """Updates a list of plugins that the frontend can include dynamically then.

        This can be different from frontend to frontend. Easiest way is to create a Javascript
        module that exports an [array] of paths that point to modules that e.g. webpack then imports.
        :param plugins_list: a list of strings that point to Javascript modules.
        """
