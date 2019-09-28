from typing import List

from gdaps import Interface


class IFrontendEngine(Interface):
    class Meta:
        # FrontendEngines should not be instantiated.
        service = False

    """a name of the frontend which can be used by GDAPS, e.g. 'vue', 'react', etc."""
    name = None

    """A list of (relative) file names that should be copied to the target directory."""
    files = []

    @staticmethod
    def initialize(frontend_path: str):
        """Initializes engine.

        This method is called when the frontend is created, and will be only called once.
        It should install all frontend specific stuff, e.g. using Js libraries using 'yarn/npm install' etc.
        """

    @staticmethod
    def update_plugins_list(plugins_list: List[str]) -> None:
        """Updates a list of plugins that the frontend can include dynamically then.

        This can be different from frontend to frontend. Easiest way is to create a Javascript
        module that exports an [array] of paths that point to modules that e.g. webpack then imports.
        :param plugins_list: a list of paths that point to Javascript modules.
        """
