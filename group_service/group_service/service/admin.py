from django.contrib import admin
from . import models

# Register models in the admin panel for easy access.
admin.site.register(models.Group)
admin.site.register(models.Role)
admin.site.register(models.UserToGroup)
