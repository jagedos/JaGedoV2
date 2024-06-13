from django.contrib import admin
from experts.models import Milestones
# Register your models here.
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'updated_at', 'created_at')
admin.site.register(Milestones, MilestoneAdmin)
