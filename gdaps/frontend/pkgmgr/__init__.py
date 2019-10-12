from django.core.management import CommandError

import gdaps
from gdaps.frontend import IPackageManager, frontend_settings

__current_pm: IPackageManager or None = None


def current_package_manager() -> IPackageManager:
    """Returns the current package manager.

    It caches the result for faster access.
    """
    name = frontend_settings.FRONTEND_PKG_MANAGER
    global __current_pm
    if __current_pm:
        return __current_pm

    assert len(IPackageManager) > 0, "No Package manager plugins found."
    for pm in IPackageManager:
        if pm.name == name:
            __current_pm = pm
            return pm
    else:
        raise CommandError(
            f"'FRONTEND_PKG_MANAGER' settings has invalid value: '{name}' not found."
        )


class NpmPackageManager(IPackageManager):
    name = "npm"

    def init(self, cwd, version=gdaps.__version__, description="", license=None):
        exec_str = f"npm init --yes --init-version='{version}' >/dev/null"
        if license:
            exec_str += f" --license'{license}'"
        if description:
            exec_str += f" --description '{description}'"
        self._exec(exec_str, cwd)

    def install(self, pkg, cwd):
        self._exec(f"npm install {pkg}", cwd)

    def installglobal(self, pkg):
        self._exec(f"npm install --global {pkg}")

    def uninstall(self, pkg, cwd):
        self._exec(f"npm uninstall {pkg}", cwd)


class YarnPackageManager(IPackageManager):
    name = "yarn"

    def init(self, cwd, version=gdaps.__version__, description="", license=None):
        self._exec("yarn init", cwd)

    def install(self, pkg, cwd):
        self._exec(f"yarn add {pkg}", cwd)

    def installglobal(self, pkg):
        self._exec(f"yarn global add {pkg}")

    def uninstall(self, pkg, cwd):
        self._exec(f"yarn remove {pkg}", cwd)
