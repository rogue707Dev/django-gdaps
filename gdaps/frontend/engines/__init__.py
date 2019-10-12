from django.core.management import CommandError
from gdaps import Interface

from gdaps.frontend import frontend_settings
from gdaps.frontend.api import IPackageManager


class NpmPackageManager(IPackageManager):
    name = "npm"
    init = "npm init"
    install = "npm install {pkg}"
    installglobal = "npm install --global {pkg}"


class YarnPackageManager(IPackageManager):
    name = "yarn"
    init = "yarn init"
    install = "yarn add {pkg}"
    installglobal = "yarn global add {pkg}"


def current_package_manager() -> IPackageManager:
    name = frontend_settings.FRONTEND_PKG_MANAGER
    for pm in IPackageManager:
        if pm.name == name:
            return pm
    else:
        raise CommandError(
            f"'FRONTEND_PKG_MANAGER' settings has invalid value: '{name}' not found."
        )
