"""
GDAPS - Generic Django Apps Plugin System
Copyright (C) 2018 Christian González

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
from typing import List

__all__ = ["PluginError", "Interface", "implements"]

logger = logging.getLogger(__name__)


class PluginError(Exception):
    """An Exception that marks an error in a plugin specific setting."""


class InterfaceMeta(type):
    """Metaclass for Interface

    This class assigns a new empty implementations and permissions list to each
    Interface at creation time.
    """
    def __new__(mcs, name, bases, dct):
        """Creates a new Interface class"""
        interface = type.__new__(mcs, name, bases, dct)
        interface._implementations = []
        interface._permissions = []
        return interface

    def __iter__(mcs):
        """Makes Interface iterable."""
        return iter(mcs._implementations)


class Interface(metaclass=InterfaceMeta):
    """Base class for interface definitions."""
    def __new__(cls, *args, **kwargs):
        raise PluginError("Interface can't be instantiated directly".format(
            cls.__class__.__name__))


class Implements:
    """Decorator class for implementing interfaces.

    Just decorate a class with *@implements(IMyInterface)*
    """

    def __init__(self, *interfaces: List[Interface]):
        """Called at declaration if the decorator (with following class).
        :param interfaces: list of interface classes the decorated class will
                be implementing.
        """
        # memoize a list of *Interface*s the decorated class is going to
        # implement
        if not interfaces:
            raise PluginError('You have to specify an <Interface>'
                              ' to @implements.')
        for iface in interfaces:
            if iface.__name__ == 'Interface':
                raise PluginError('You can\'t directly implement <Interface>.'
                                  'Please subclass <Interface> and use that'
                                  'class as parameter for @implements().')

        self._interfaces = interfaces

    def __call__(self, cls):
        """Called at decoration
        :param cls: decorated class
        """
        # add the decorated class to each Interface's internal
        # implementation list
        for iface in self._interfaces:
            iface._implementations.append(cls)

        return cls


implements = Implements
