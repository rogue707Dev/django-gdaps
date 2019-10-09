from gdaps import Interface


@Interface
class IGrapheneQuery:
    """Interface class to collect all graphene queries

    Any GDAPS plugin that exposes data to the GraphQL API must implement this
    Interface. Have a look at
    http://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/#hello-graphql-schema-and-object-types
    how to create abstract Graphene query objects. You just need to subclass IGrapheneQuery,
    and they are included into the global GraphQL API automatically.
    """

    __service__ = False


@Interface
class IGrapheneMutation:
    """Interface class to collect all graphene mutations

    Any GDAPS plugin that creates data mutations for the GraphQL API must implement this
    Interface. Have a look at
    http://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/#hello-graphql-schema-and-object-types
    how to create abstract Graphene mutation objects. You just need to subclass IGrapheneMutation,
    and they are included into the global GraphQL API automatically.
    """

    __service__ = False
