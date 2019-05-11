from gdaps import Interface


class IGrapheneQuery(Interface):
    """Interface decorator class to collect all graphene queries

    Any GDAPS plugin that exposes data to the GraphQL API must implement this
    Interface. Have a look at
    http://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/#hello-graphql-schema-and-object-types
    how to create abstract Graphene query objects. You just need to decorate them with @IGrapheneQuery,
    and they are included into the global GraphQL API automatically.
    """
