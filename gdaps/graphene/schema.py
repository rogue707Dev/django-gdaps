import graphene

from gdaps import PluginError
from gdaps import implements, ExtensionPoint
from gdaps.graphene.interfaces import IGrapheneQuery
from gdaps.pluginmanager import PluginManager


PluginManager.load_plugin_submodule("schema")
ep = ExtensionPoint(IGrapheneQuery)
if len(ep) > 0:
    GDAPSQuery = type("GDAPSQuery", tuple(ep) + (graphene.ObjectType,), {})
else:
    raise PluginError(
        "No plugin implements the <IGrapheneQuery> interface. To use gdaps.graphene, you have to create "
        "at least one schema.py file in a plugin and create a Graphene Query there."
    )
