import graphene
from graphene.utils.subclass_with_meta import SubclassWithMeta_Meta

from gdaps import Interface, InterfaceMeta


@Interface
class IGraphenePlugin:
    """Interface class to collect all graphene queries/mutations

    Any GDAPS plugin that exposes data to the GraphQL API must implement this
    Interface. Have a look at
    http://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/#hello-graphql-schema-and-object-types
    how to create abstract Graphene query objects. You just need to subclass IGrapheneObject,
    and they are included into the global GraphQL API automatically.
    """

    __service__ = False
    query: type(graphene.ObjectType) = None
    mutation: type(graphene.ObjectType) = None
