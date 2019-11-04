# GDAPS Graphene support

GDAPS supports Django-Graphene out of the box, and eases working with it.

To enable it, add `graphene_django` and `gdaps.graphene` to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ...
    "graphene_django",
    "gdaps.graphene"
    "gdaps",
]
```

It introduces an `IGrapheneSchema` interface that you must use for creating queries and mutations which are automatically found and installed. Just create a `schema.py`file and any of your graphene queries/mutations like:

```python
import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType

from gdaps.graphene.api import IGrapheneSchema


class UserType(DjangoObjectType):
    """Django's built-in User type"""

    class Meta:
        model = User


class UserQuery:
    users = graphene.List(UserType)

    @staticmethod
    def resolve_users(self, info, **kwargs):
        return User.objects.all()

# Here comes the magic:
class UserSchema(IGrapheneSchema):
    query = UserQuery
```


Side note: you have to create at least one *schema.py* implementing `IGrapheneSchema`. If gdaps.graphene finds no plugin implementing it, it raises a PluginError.

All plugins inheriting from IGrapheneSchema are automatically found and exposed in your application API.
You just need add your Graphene URL to your root urls.py as usual, and use GDAPSQuery and GDAPSMutation as parameters for the view.
```python

import graphene
from gdaps.graphene.schema import GDAPSQuery, GDAPSMutation
from gdaps.pluginmanager import PluginManager
from django.urls import path
from graphene_django.views import GraphQLView

PluginManager.load_plugin_submodule("schema")
schema = graphene.Schema(query=GDAPSQuery, mutation=GDAPSMutation)

urlpatterns = [
    # ...
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]

```

For more info how to create Graphene queries, look at the [Graphene-Django documentation](http://docs.graphene-python.org/projects/django/en/latest/)
