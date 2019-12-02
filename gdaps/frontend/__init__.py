import logging

from gdaps.exceptions import PluginError
from gdaps.frontend.api import IPackageManager
from .api import IFrontendEngine, IPackageManager
from .conf import frontend_settings
import gdaps.frontend.engines

default_app_config = "gdaps.frontend.apps.FrontendConfig"
logger = logging.getLogger(__name__)

__current_engine: IFrontendEngine or None = None


def current_engine() -> IFrontendEngine:
    """Returns the current frontend engine.

    It caches the result for faster access.
    """

    global __current_engine
    if __current_engine:
        return __current_engine

    for engine in IFrontendEngine:
        if engine.name == frontend_settings.FRONTEND_ENGINE:
            __current_engine = engine
            return engine
    else:
        raise PluginError(
            "No frontend engine is selected. Please select one in settings.py using GDAPS['FRONTEND_ENGINE']. "
            f"Available engines are: {[engine.name for engine in IFrontendEngine]}"
        )
