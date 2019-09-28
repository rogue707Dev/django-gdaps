from django.conf import settings
from django.contrib import admin

from gdaps.conf import gdaps_settings
from gdaps.models import GdapsPlugin


class ReadOnlyAdmin(admin.ModelAdmin):
    """This is a ModelAdmin class that sets the whole GDAPS model readonly."""

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in obj._meta.fields]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class GdapsInline(admin.TabularInline):
    pass


class GdapsAdmin(ReadOnlyAdmin):
    """ModelAdmin class for GDAPS plugins."""

    list_display = [
        "verbose_name",
        "version",
        "author",
        "visible",
        "enabled",
        "category",
    ]
    sortable_by = ["category", "visible", "enabled"]

    def get_readonly_fields(self, request, obj=None):
        return [
            name
            for name in super().get_readonly_fields(request, obj)
            if not name in ["enabled", "visible"]
        ]


# show Admin per default, disable this behaviour using:
# GDAPS["ADMIN"] = False
# in settings.py
if gdaps_settings.ADMIN:
    admin.site.register(GdapsPlugin, GdapsAdmin)
