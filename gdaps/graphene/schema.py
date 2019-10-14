import graphene

from gdaps.exceptions import PluginError
from gdaps.graphene.api import IGraphenePlugin
from gdaps.pluginmanager import PluginManager

__all__ = ["GDAPSQuery", "GDAPSMutation"]


class __EmptyQuery(graphene.ObjectType):
    """Empty GraphQL query"""


class __EmptyMutation(graphene.ObjectType):
    """Empty GraphQL mutation"""


"""A Graphene query object that collects all plugins' Graphene query objects."""
GDAPSQuery = None

GDAPSMutation = None
"""A Graphene mutation object that collects all plugins' Graphene mutation objects."""

PluginManager.load_plugin_submodule("schema")

if len(IGraphenePlugin) > 0:
    query_objects = tuple(
        [obj.query for obj in IGraphenePlugin if obj.query is not None]
    )
    GDAPSQuery = type(
        "GDAPSQuery", query_objects + (__EmptyQuery, graphene.ObjectType), {}
    )
    mutation_objects = tuple(
        [obj.mutation for obj in IGraphenePlugin if obj.mutation is not None]
    )
    if mutation_objects:
        GDAPSMutation = type(
            "GDAPSMutation",
            mutation_objects + (__EmptyMutation, graphene.ObjectType),
            {},
        )


else:
    raise PluginError(
        "No plugin implements the <IGrapheneObject> interface. "
        "Create a schema.py file in a plugin and create one there."
    )
