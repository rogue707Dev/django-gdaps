# this is the API of GDAPS itself.
from gdaps import Interface


class IFrontendEngine(Interface):
    name = None
    @staticmethod
    def initialize(frontend_path: str):
        pass
