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

    """A list of tuples for file endings that should be converged."""
    rewrite_template_suffixes = (
        # Allow shipping invalid .js files without linting errors.
        (".js-tpl", ".js"),
    )

    """Allowed extensions which are rendered."""
    extensions = ("js",)

    @staticmethod
    def initialize(frontend_dir: str):
        """Initializes engine.

        This method is called when the frontend is created, and will be only called once.
        It should install all frontend specific stuff, e.g. using Js libraries using 'yarn/npm install' etc.
        It can assume that the BASE_DIR/frontend_dir/ exists.
        :param frontend_dir: relative directory within BASE_DIR where the frontend lives.

        """

    @staticmethod
    def update_plugins_list(plugin_names: List[str]) -> None:
        """Updates a list of plugins that the frontend can include dynamically then.

        This can be different from frontend to frontend. Easiest way is to create a Javascript
        module that exports an [array] of paths that point to modules that e.g. webpack then imports.
        :param plugin_names: a list of module names that contain a frontend directory with a Javascript module.
        """
