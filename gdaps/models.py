from django.db import models


class GdapsPlugin(models.Model):

    name = models.CharField(max_length=255)
    verbose_name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    # vendor?
    # author_email?
    description = models.TextField(null=True, default=None)
    visible = models.BooleanField(default=True)
    version = models.CharField(max_length=32, default="1.0.0")
    compatibility = models.CharField(max_length=255, null=True, default=None)
