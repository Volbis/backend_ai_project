from django.contrib import admin
import back.models as models

# Register your models here.
admin.site.register(models.Dossier)
admin.site.register(models.Document)
admin.site.register(models.Report)