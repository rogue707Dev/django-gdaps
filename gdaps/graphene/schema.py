import graphene

from gdaps import PluginError
from gdaps import ExtensionPoint
from gdaps.graphene.interfaces import IGrapheneQuery, IGrapheneMutation
from gdaps.pluginmanager import PluginManager

__all__ = ["GDAPSQuery", "GDAPSMutation"]


class EmptyQuery(graphene.ObjectType):
    """Empty GraphQL query"""


class EmptyMutation(graphene.ObjectType):
    """Empty GraphQL mutation"""


PluginManager.load_plugin_submodule("schema")

ep = ExtensionPoint(IGrapheneQuery)
if len(ep) > 0:
    GDAPSQuery = type("GDAPSQuery", tuple(ep) + (EmptyQuery, graphene.ObjectType), {})
else:
    raise PluginError(
        "No plugin implements the <IGrapheneQuery> interface. "
        "Create a schema.py file in a plugin and create a Graphene Query there."
    )


ep = ExtensionPoint(IGrapheneMutation)
if len(ep) > 0:
    GDAPSMutation = type("GDAPSMutation", tuple(ep) + (graphene.ObjectType,), {})
else:
    GDAPSMutation = None
