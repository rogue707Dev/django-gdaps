from gdaps import Interface

__all__ = ["ITestInterface1", "ITestInterface2", "TestPlugin"]

class ITestInterface1(Interface):
    pass


class ITestInterface2(Interface):
    def get_item(self):
        pass

class TestPlugin:
    pass