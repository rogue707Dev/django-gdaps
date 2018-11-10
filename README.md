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
* Apps can use their own URLs (they are included automatically)
* Apps can define Interfaces, that other GDAPS apps can implement (these are automatically found) 

## Usage

Just create a normal Django application, e.g. using `manage.py startproject myproject`.

Now install `gdaps` as usual:

```python
from gdaps.pluginmanager import PluginManager

INSTALLED_APPS = [
    # ... standard Django apps and GDAPS
    'gdaps',
]
```

The configuration of GDAPS is bundled in one variable:

```python
GDAPS = {
  'PLUGIN_PATH': 'myproject.plugins',
}

# Load all plugins from setuptools entry points named 'myproject.plugins'
INSTALLED_APPS += PluginManager.find_plugins()

```
Basically, this is all you really need so far, for a minimum working GDAPS-enabled Django application.


### Creating plugins

You can create plugins in any directory of your Django app. However, we recommend that you choose a folder named *plugins*, for convenience.
As explained in the [Static plugins](#static-plugins) section, you can refer to these plugins then directly in the `INSTALLED_APPS` settings variable. 

To ease the task of creating plugins, GDAPS provides a Django management command named `startplugin`:

    ./manage.py startplugin fooplugin

This command asks a few questions, creates a basic Django app in the `PLUGIN_PATH` you chose before, and provides useful defaults as well as a setup.py file. If you use git in your project, and have the `gitpython` module installed (`pip install gitpython`), it will determine your git user name and email automatically and use it for the setup.py file.

You now can add this plugin statically to `INSTALLED_APPS` - see [Static plugins](#static-plugins). Or you can make use of the dynamic loading - see [Dynamic plugins](#dynamic-plugins).

### Static plugins

In most of the cases, you will ship your application with a few "standard" plugins that are statically installed.
These plugins should be loaded *after* the `gdaps` app. Use the PLUGIN_PATH you created before.

```python
# ...

INSTALLED_APPS = [
    # ... standard Django apps and GDAPS
    'gdaps',

    # just put "static" plugins here too:
    'myproject.plugins.fooplugin',
]
```

We recommend that you use 'myproject.**plugins**' as entrypoint, this way you can
use myproject.plugins.fooplugin as dotted appname, no matter whether you put the app
into your real "static" `myproject/plugins/fooplugin` folder, or provide it via PyPi.
You can use anything you want, but don't forget to use that name as folder name 
within your project too, so that the Python path names are the same.


### Dynamic plugins
By cd'ing into the `plugins` directory and installing it locally with pip/pipenv, you can make your application aware of that plugin:

```bash
cd fooplugin
pipenv install -e .
```

This installs the plugin as python module into the site-packages and makes it discoverable using setuptools. From
this moment on it should be already registered and loaded after a Django server restart.
Of course this also works when plugins are installed standalone, they don't have to be in the `plugins` folder. You can conveniently start developing plugins in there, and later upload them as separate plugins to PyPi, making them installable easily.

### Using GDAPS apps

#### Interfaces

Plugins can define interfaces, which can then be implemented by other plugins. If you create a plugin using 
`./manage.py startplugin`, it will create a `<app_name>/api/interfaces.py` file automatically. You can create interfaces 
there.

```python
from gdaps import Interface

class IMySpecialFoopluginInterface(Interface):   
    """Documentation of the interface"""
    
    def do_something(self):
        pass
```

You can then easily implement this interface in any other file (in this plugin or in another plugin) using the 
`implements` decorator syntax:

```python
from gdaps import implements
from myproject.plugins.fooplugin.api.interfaces import IMySpecialFoopluginInterface

@implements(IMySpecialFoopluginInterface)
class OtherPluginClass:
    def do_something(self):
        print('I did something!')
```


#### URLs

To let your plugin define some URLs that are automatically detected, you have to add some code to the global urls.py file:

```python
from gdaps.pluginmanager import PluginManager 

urlpatterns =  [
    # ...
]

# just add this line after the urlpatterns definition:
urlpatterns += PluginManager.collect_urls()
```

GDAPS then loads and imports all available plugins' urls.py files, collects
their `urlpatterns` variables and merges them into the global one.

A typical `fooplugin/urls.py` would look like this:

    from . import views
    
    app_name = fooplugin

    urlpatterns =  [
        path('/fooplugin/myurl', views.MyUrlView.as_view()),
    ]

GDAPS lets your plugin create global, root URLs, they are not namespaced. This is because soms plugins need to create URLS for frameworks like DRF, etc.

## Settings

GDAPS settings are bundled in a `GDAPS` variable you can add to your settings.py. The defaults are:
```python
GDAPS = {
    'PLUGIN_PATH': 'plugins'
}
```

Explanations of the settings:

##### PLUGIN_PATH

This is the (dotted) plugin path used as directory within your main application, and as entry point for setuptools' plugins. The default is 'plugins', so if you name your project "my_project", there will be a `my_project/plugins/` directory where e.g. `./manage.py startplugin` will create its content.


### Custom per-plugin settings

GDAPS allows your application to have own settings for each plugin easily, which provide defaults, and can be overridden in the global `settings.py` file. Look at an example conf.py file (created by `./manage.py startplugin fooplugin`):

```python
from django.test.signals import setting_changed
from gdaps.conf import PluginSettings

NAMESPACE = 'FOOPLUGIN'

# Optional defaults. Leave empty if not needed.
DEFAULTS = {
    'MY_SETTING': 'somevalue',
    'FOO_PATH': 'django.blah.foo',
    'BAR': [
        'baz',
        'buh',
    ],
}

# Optional list of settings that are allowed to be in 'string import' notation. Leave empty if not needed.
IMPORT_STRINGS = (
    'myproject.plugins.fooplugin.models.FooModel'
)

# Optional list of settings that have been removed. Leave empty if not needed.
REMOVED_SETTINGS = ( 'FOO_SETTING' )


fooplugin_settings = PluginSettings('FOOPLUGIN', None, DEFAULTS, IMPORT_STRINGS)


def reload_fooplugin_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'FOOPLUGIN':
        fooplugin_settings.reload()


setting_changed.connect(reload_fooplugin_settings)
``` 

Detailed explanation:

##### `DEFAULTS`
The `DEFAULTS` are, as the name says, a default array of settings. If `fooplugin_setting.BLAH is not set by the user, this default value is used.

##### `IMPORT_STRINGS`
Settings in a *dotted* notation are evaluated, they return not the string, but the object they point to.
If it does not exist, an `ImportError` is raised.
 
##### `REMOVED_SETTINGS`
A list of settings that are forbidden to use. If accessed, an `RuntimeError` is raised.


This allows very flexible settings - as dependant plugins can easily import the `fooplugin_settings` from your `conf.py`.

However, the created conf.py file is not needed, so if you don't use custom settings at all, just delete the file.

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
