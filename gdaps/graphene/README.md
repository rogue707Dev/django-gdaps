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

It introduces an `IGrapheneQuery` interface that you must use for creating Queries which are automatically found and installed. Just create a `schema.py`file and decorate any of your Graphene queries like:

```python
import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType

from gdaps import implements
from gdaps.graphene.interfaces import IGrapheneQuery


class UserType(DjangoObjectType):
    """Django's built-in User type"""

    class Meta:
        model = User


@implements(IGrapheneQuery)
class UserQuery:
    users = graphene.List(UserType)

    @staticmethod
    def resolve_users(self, info, **kwargs):
        return User.objects.all()
```

Side note: you have to create at least one Query implementing `IGraphQuery`. If gdaps.graphene finds no plugin implementing it, it raises a PluginError. This is due to a small limitation in graphene_django. PRs welcome ;-).

For more info how to create Graphene queries, look at the [Graphene-Django documentation](http://docs.graphene-python.org/projects/django/en/latest/)
