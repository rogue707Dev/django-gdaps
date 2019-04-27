from gdaps import implements
from tests.plugins.plugin1.api import FirstInterface


@implements(FirstInterface)
class Foo:
    def first_method(self):
        return "first"
