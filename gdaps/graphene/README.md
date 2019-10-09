# GDAPS Graphene support

GDAPS supports Django-Graphene out of the box, and eases working with it.

To enable it, add graphene_django and gdaps.graphene to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ...
    "graphene_django",
    "gdaps",
    "gdaps.graphene"
]
```

It introduces an `IGrapheneQuery` interface that you must use for creating Queries which are automatically found and installed. Just create a `schema.py`file and any of your Graphene queries like:

```python
import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType

from gdaps.graphene.interfaces import IGrapheneQuery


class UserType(DjangoObjectType):
    """Django's built-in User type"""

    class Meta:
        model = User


class UserQuery(IGrapheneQuery):
    users = graphene.List(UserType)

    @staticmethod
    def resolve_users(self, info, **kwargs):
        return User.objects.all()
```

Side note: you have to create at least one Query implementing `IGraphQuery`. If gdaps.graphene finds no plugin implementing it, it raises a PluginError. This is due to a small limitation in graphene_django. PRs welcome ;-).

Now add your Graphene URL to your root urls.py:
```python

import graphene
from gdaps.graphene import GDAPSQuery
from gdaps.pluginmanager import PluginManager

PluginManager.load_plugin_submodule("schema")
schema = graphene.Schema(query=GDAPSQuery)

urlpatterns = [
    # ...
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=GDAPSQuery)),
]

```

For more info how to create Graphene queries, look at the [Graphene-Django documentation](http://docs.graphene-python.org/projects/django/en/latest/)
