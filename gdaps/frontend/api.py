from gdaps import Interface


class IFrontendEngine(Interface):
    class Meta:
        service = False

    name = None
    files = []

    @staticmethod
    def initialize(frontend_path: str):
        pass
