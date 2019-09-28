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
        """Initializes the frontend, e.g. calls npm/yarn to install required packages."""

    @staticmethod
    def syncplugins(frontend_path):
        """Synchronizes plugins with DB and entry points.

        This method should gather all plugins and add them to the database.
        Additionally, it should maintain a central list of plugin entry points of the
        frontend parts of each plugin, and create e.g. a plugins.js file which is then
        consumed by the frontend core."""
