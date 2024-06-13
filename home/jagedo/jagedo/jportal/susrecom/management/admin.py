from django.contrib import admin
from management.models import Counties, PickUps

# Register your models here.
class CountiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'updated_at', 'created_at')

admin.site.register(Counties, CountiesAdmin)


class PickUpsAdmin(admin.ModelAdmin):
    list_display = ('county', 'name','status', 'updated_at', 'created_at')

admin.site.register(PickUps, PickUpsAdmin)
