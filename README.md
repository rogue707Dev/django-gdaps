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

All the GDAPS plugins you create should be loaded *after* the (statically defined) INSTALLED_APPS.
So add the plugin directory to the global settings, after INSTALLED_APPS, and load all
the plugins:

```python
from gdaps.pluginmanager import PluginManager

# ...

INSTALLED_APPS = [
    # ... standard Django apps and GDAPS
    'gdaps',
    
    # put "static" plugins here too:
    'myproject.plugins.fooplugin', 
]

# load all plugins from setuptools entry points named 'myproject.plugins' 
PLUGINS = PluginManager.find_plugins('myproject.plugins')
INSTALLED_APPS += PLUGINS

```

We recommend that you use 'myproject.**plugins**' as entrypoint, this way you can
use myproject.plugins.fooplugin as dotted appname, no matter whether you put the app
into your real "static" `myproject/plugins/fooplugin` folder, or provide it via PyPi.
You can use anything you want, but don't forget to use that name as folder name 
within your project too, so that the Python path names are the same.

This is all you really need so far, for a minimum working GDAPS-enabled Django application.


### Interfaces

Plugins can define interfaces, which can then be implemented by other plugins.

```TODO: Interfaces example```

There are other things you can tweak:


### URLs

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
        path('/fooplugin/myurl', views.MyUrlView.as_view()),g
    ]

GDAPS lets your plugin create global, root URLs, they are not namespaced. This is because soms plugins need to create URLS for frameworks like DRF, etc.

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