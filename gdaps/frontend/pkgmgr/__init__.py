import subprocess

from django.core.management import CommandError

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
            return pm
    else:
        raise CommandError(
            f"'FRONTEND_PKG_MANAGER' settings has invalid value: '{name}' not found."
        )


class NpmPackageManager(IPackageManager):
    name = "npm"

    init = "npm init"
    install = "npm install {pkg}"
    installglobal = "npm install --global {pkg}"
    uninstall = "npm uninstall {pkg}"


class YarnPackageManager(IPackageManager):
    name = "yarn"
    init = "yarn init"
    install = "yarn add {pkg}"
    installglobal = "yarn global add {pkg}"
    uninstall = "yarn remove {pkg}"
