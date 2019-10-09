import graphene

from gdaps.exceptions import PluginError
from gdaps.graphene.interfaces import IGrapheneQuery, IGrapheneMutation
from gdaps.pluginmanager import PluginManager

__all__ = ["GDAPSQuery", "GDAPSMutation"]


class EmptyQuery(graphene.ObjectType):
    """Empty GraphQL query"""


class EmptyMutation(graphene.ObjectType):
    """Empty GraphQL mutation"""


PluginManager.load_plugin_submodule("schema")

if len(IGrapheneQuery) > 0:
    GDAPSQuery = type(
        "GDAPSQuery", tuple(IGrapheneQuery) + (EmptyQuery, graphene.ObjectType), {}
    )
else:
    raise PluginError(
        "No plugin implements the <IGrapheneQuery> interface. "
        "Create a schema.py file in a plugin and create a Graphene query there."
    )


if len(IGrapheneMutation) > 0:
    GDAPSMutation = type(
        "GDAPSMutation", tuple(IGrapheneMutation) + (graphene.ObjectType,), {}
    )
else:
    GDAPSMutation = None
