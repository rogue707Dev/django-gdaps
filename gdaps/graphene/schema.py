import graphene

from gdaps.exceptions import PluginError
from gdaps.graphene.api import IGrapheneSchema
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

if len(IGrapheneSchema) > 0:
    query_objects = tuple(
        [obj.query for obj in IGrapheneSchema if obj.query is not None]
    )
    GDAPSQuery = type(
        "GDAPSQuery", query_objects + (__EmptyQuery, graphene.ObjectType), {}
    )
    mutation_objects = tuple(
        [obj.mutation for obj in IGrapheneSchema if obj.mutation is not None]
    )
    if mutation_objects:
        GDAPSMutation = type(
            "GDAPSMutation",
            mutation_objects + (__EmptyMutation, graphene.ObjectType),
            {},
        )


else:
    GDAPSQuery = None
    GDAPSMutation = None
