Introduction
============

This library allows Django to make real "pluggable" apps.

A standard Django "app" is *reusable* (if done correctly), but is not *pluggable*,
like being distributed and "plugged" into a Django main application without modifications. GDAPS is filling this gap.

The reason you want to use GDAPS is: **you want to create an application that should be extended via plugins**. GDAPS consists of a few bells and twistles where Django lacks "automagic":

GDAPS apps...
* are automatically found using setuptools' entry points
* can provide their own URLs which are included and merged into urlpatterns automatically
* can define ``Interfaces``, that other GDAPS apps then can implement
* can provide Javascript frontends that are found and compiled automatically (WorkInProgress)



