from gdaps import Interface


class IFrontendEngines(Interface):
    name = None
    files = []

    def initialize(self):
        pass
