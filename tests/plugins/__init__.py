from tests.plugins.plugin1.api import FirstInterface


class Foo(FirstInterface):
    def first_method(self):
        return "first"
