# GDAPS - Generic Django Apps Plugin System

This library allows Django to make real "pluggable" apps.

A standard Django "app" is *reusable* (if done correctly), but is not really pluggable,
like being distributed and "plugged" into a Django main application without modifications.

    CAVE: This software is in a very early development state. 
    It could eat your dog, or create wormholes below your bed.
    Use it at your own risk. You have been warned.

If you want to create a Django application that makes use of "plugins" that can extend your project later,
this library is right for you. It consists of a few bells and twistles where Django lacks "automagic":

* Apps are automatically found using pkgtools' entry points
* Apps can provide their own URLs (they are included and merged into urlpatterns automatically)
* Apps can define `Interfaces`, that other GDAPS apps then can implement
* Apps can provide Javascript frontends that are found and compiled automatically (WorkInProgress)

## Usage

Create a Django application as usual: `manage.py startproject myproject`.

Now install `gdaps` as usual app:

```python
from gdaps.pluginmanager import PluginManager

INSTALLED_APPS = [
    # ... standard Django apps and GDAPS
    "gdaps",
    # if you also want frontend support, add:
    #"gdaps.frontend"
    # "myproject.plugins.fooplugin",
    # "webpack_loader",
]
# The following line is important: It loads all plugins from setuptools 
# entry points and from the directory named 'myproject.plugins':
INSTALLED_APPS += PluginManager.find_plugins("myproject.plugins")
```
We recommend that you use 'myproject.**plugins**' or just '**plugins**'.

For further frontend specific instructions, see [Frontend support](#frontend-support).

The configuration of GDAPS is bundled in one namespace `GDAPS`:

```python
GDAPS = {
    "FRONTEND_DIR": "frontend",
}
```
Also see [Settings](#settings]).

Basically, this is all you really need so far, for a minimal working GDAPS-enabled Django application.

### Creating plugins

Create plugins using a Django management command:

    ./manage.py startplugin fooplugin

This command asks a few questions, creates a basic Django app in the `FRONTEND_DIR` you chose before, and provides useful defaults as well as a setup.py file. 

If you use git in your project, install the `gitpython` module (`pip/pipenv install gitpython --dev`). `startplugin` will determine your git user/email automatically and use it for the setup.py file.

You now have two choices for this plugin:
 * add it statically to `INSTALLED_APPS`: see [Static plugins](#static-plugins).
 * make use of the dynamic loading feature: see [Dynamic plugins](#dynamic-plugins).

### Static plugins

In most of the cases, you will ship your application with a few "standard" plugins that are statically installed.
These plugins must be loaded *after* the `gdaps` app.

```python
# ...

INSTALLED_APPS = [
    # ... standard Django apps and GDAPS
    "gdaps",

    # put "static" plugins here too:
    "myproject.plugins.fooplugin",
]
```
This app is laoded as usual, bug your GDAPS enhanced Django application can make use of it's features.

### Dynamic plugins
By installing a plugin with pip/pipenv, you can make your application aware of that plugin too:

```bash
pipenv install -e myproject/plugins/fooplugin
```

This installs the plugin as python module into the site-packages and makes it discoverable using setuptools. From
this moment on it should be already registered and loaded after a Django server restart.
Of course this also works when plugins are installed from PyPi, they don't have to be in the project's `plugins` folder. You can conveniently start developing plugins in there, and later move them to the PyPi repository.

### Using GDAPS apps

#### Interfaces

Plugins can define interfaces, which can then be implemented by other plugins. The `startplugin` command will create a `<app_name>/api/interfaces.py` file automatically. Interfaces must not be defined in that module, but it is a recommended coding style for GDAPS plugins:

```python
from gdaps import Interface

class IFooInterface(Interface):   
    """Documentation of the interface"""
    
    def do_something(self):
        pass
```

#### Implementations

You can then easily implement this interface in any other file (in this plugin or in another plugin) using the 
`@implements` decorator syntax:

```python
from gdaps import implements
from myproject.plugins.fooplugin.api.interfaces import IFooInterface

@implements(IFooInterface)
class OtherPluginClass:

    def do_something(self):
        print('I did something!')
```

I didn't want to force implementations to inherit a `Plugin` base class, like some other plugin systems do.
This would mean that implementations won't be as flexible as I wanted them. When just using a decorator, you can easily
use ANY, even your already existing, class and just ducktype-implement the methods the Interface demands. If you forget 
to implement a method, GDAPS will complain instantly.  

If you need a more "Plugin"-like class, just create a class that implements the `gdaps.IPlugin` interface, or use the
included `gdaps.Plugin` class as parent for your convenience.


#### ExtensionPoints

An ExtensionPoint (EP) is a plugin hook that refers to an Interface. An EP can be defined anywhere in code.
You can then get all the plugins that implement that interface by just iterating over that ExtensionPoint:

 ```python
from gdaps import ExtensionPoint
from myproject.plugins.fooplugin.api.interfaces import IFooInterface

class MyPlugin:
    ep = ExtensionPoint(IFooInterface)
    
    def foo_method(self):
        for plugin in ep:
            print plugin().do_domething()
```

Keep in mind that iterating over an ExtensionPoint **does not return instances** of plugins. It just returns the **class** that was decorated with *@implements*. This might be improved in the future (auto-instantiated plugins).


#### URLs

To let your plugin define some URLs that are automatically detected, you have to add some code to the global urls.py file:

```python
from gdaps.pluginmanager import PluginManager 

urlpatterns =  [
    # ...
]

# just add this line after the urlpatterns definition:
urlpatterns += PluginManager.urlpatterns()
```

GDAPS then loads and imports all available plugins' urls.py files, collects
their `urlpatterns` variables and merges them into the global one.

A typical `fooplugin/urls.py` would look like this:

```python
from . import views

app_name = fooplugin

urlpatterns =  [
    path("/fooplugin/myurl", views.MyUrlView.as_view()),
]
```

GDAPS lets your plugin create global, root URLs, they are not namespaced. This is because soms plugins need to create URLS for frameworks like DRF, etc. Plugins are responsible for their URLs, and that they don't collide with others.

## Settings

GDAPS settings are bundled in a `GDAPS` variable you can add to your settings: 
```python
GDAPS = {
    "FRONTEND_DIR": "frontend"
}
```

##### `FRONTEND_DIR`
The absolute path to the application wide frontend directory, where all plugin's frontend parts will be bundled later.

*Defaults to:* `os.path.join(settings.BASE_DIR, "frontend")`


### Custom per-plugin settings

GDAPS allows your application to have own settings for each plugin easily, which provide defaults, and can be overridden in the global `settings.py` file. Look at the example conf.py file (created by `./manage.py startplugin fooplugin`), and adapt to your needs:

```python
from django.test.signals import setting_changed
from gdaps.conf import PluginSettings

NAMESPACE = "FOOPLUGIN"

# Optional defaults. Leave empty if not needed.
DEFAULTS = {
    "MY_SETTING": "somevalue",
    "FOO_PATH": "django.blah.foo",
    "BAR": [
        "baz",
        "buh",
    ],
}

# Optional list of settings that are allowed to be in "string import" notation. Leave empty if not needed.
IMPORT_STRINGS = (
    "FOO_PATH"
)

# Optional list of settings that have been removed. Leave empty if not needed.
REMOVED_SETTINGS = ( "FOO_SETTING" )


fooplugin_settings = PluginSettings("FOOPLUGIN", None, DEFAULTS, IMPORT_STRINGS)

``` 

Detailed explanation:

##### `DEFAULTS`
The `DEFAULTS` are, as the name says, a default array of settings. If `fooplugin_setting.BLAH` is not set by the user in settings.py, this default value is used.

##### `IMPORT_STRINGS`
Settings in a *dotted* notation are evaluated, they return not the string, but the object they point to.
If it does not exist, an `ImportError` is raised.
 
##### `REMOVED_SETTINGS`
A list of settings that are forbidden to use. If accessed, an `RuntimeError` is raised.


This allows very flexible settings - as dependant plugins can easily import the `fooplugin_settings` from your `conf.py`.

However, the created conf.py file is not needed, so if you don't use custom settings at all, just delete the file.

## Frontend support

GDAPS supports Javascript frontends for building e.g. SPA applications. ATM only Vue.js ist supported, but PRs are welcome to add more (Angular, React?).

If you add `gdaps.frontend` to `INSTALLED_APPS`, there is a new management command available: `manage.py initfrontend`. It has one mandatory parameter, the frontend engine:
    
    ./manage.py initfrontend vue

This creates a /frontend/ directory in the project root. Change into that directory and run `yarn install` once to install all the dependencies of Vue.js needed.

It is recommended to install vue globally, you can do that with `yarn global add @vue/cli @vue/cli-service-global`.

Now you can start `yarn serve` in the frontend directory. This starts a development web server that bundles the frontend app using webpack automatically.
You then need to start Django using `./manage.py runserver` to enable the Django backend. GDAPS manages all the needed background tasks to transparently enable hot-reloading when you change anything in the frontend source code now.


## Contributing

If you want to contribute, feel free and write a PR, or contact me.


## License

I'd like to give back what I received from many Open Source software packages, and keep this
library as open as possible, and it should stay so.
GDAPS is licensed under the [GPL](https://www.gnu.org/licenses/gpl.html), see [LICENSE.md](LICENSE.md).


## Credits

I was majorly influenced by other plugin systems when writing this code, big thanks to them:

* The [PyUtilib](https://github.com/PyUtilib/pyutilib) library
* [The Pretix ecosystem](https://pretix.eu/)
* [Yapsy](http://yapsy.sourceforge.net/)
* [Django-Rest-Framework](https://www.django-rest-framework.org/)
* [Graphene-Django](http://docs.graphene-python.org/projects/django/en/latest/)
