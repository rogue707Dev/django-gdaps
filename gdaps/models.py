from django.db import models


class GdapsPlugin(models.Model):

    name = models.CharField(max_length=255)
    verbose_name = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    author_email = models.EmailField(blank=True)
    vendor = models.CharField(max_length=255, blank=True)
    description = models.TextField(null=True, default=None)
    version = models.CharField(max_length=32, default="1.0.0")
    compatibility = models.CharField(max_length=255, null=True, default=None)

    visible = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
