import subprocess
from typing import List

import gdaps
from gdaps import Interface


@Interface
class IFrontendEngine:
    # FrontendEngines should not be instantiated.
    __service__ = False

    """The name of the frontend which can be used by GDAPS, e.g. 'vue', 'react', etc."""
    name = None

    """A list of tuples for template file endings that should be renamed and rendered as templates."""
    rewrite_template_suffixes = ((".js-tpl", ".js"),)

    """A list of (relative) file names that also be treated as templates."""
    extra_files = []

    extensions = ()

    __package_manager = None

    @classmethod
    def initialize(cls, frontend_dir: str, package_manager: dict):
        """Initializes engine.

        This method is called when the frontend is created, and will be only called once.
        It should install all frontend specific stuff, e.g. using Js libraries using 'yarn/npm install' etc.
        It can assume that the BASE_DIR/frontend_dir/ exists.
        :param frontend_dir: relative directory within BASE_DIR where the frontend lives.

        """

    @staticmethod
    def update_plugins_list(plugin_paths: List[str]) -> None:
        """Updates a list of plugins that the frontend can include dynamically then.

        This can be different from frontend to frontend. Easiest way is to create a Javascript
        module that exports an [array] of paths that point to modules that e.g. webpack then imports.
        :param plugin_paths: a list of module names that contain a frontend directory with a Javascript module.
        """


@Interface
class IPackageManager:
    """Interface for package manager representation.

    :var name: The name of the command
    :var init: the init command to create a repository
    :var install: the command to install a package. use '{pkg}' as replacement for the package.
    :var installglobal: the command to install a package globally. use '{pkg}' as replacement for the package.
    """

    name = None

    def _exec(self, command: str, cwd: str):
        """Convenience function for implementers to exec a command in the shell."""
        subprocess.check_call(command, cwd=cwd, shell=True)

    def init(self, cwd, version=gdaps.__version__, description="", license=None):
        raise NotImplementedError

    def install(self, pkg, cwd):
        raise NotImplementedError

    def installglobal(self, pkg):
        raise NotImplementedError

    def uninstall(self, pkg, cwd):
        raise NotImplementedError
