from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Tkeys, CompanyMeta

class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'national_id', 'phone_number', 'is_staff'
        
        )

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                 'is_active', 'is_staff', 'is_superuser', 'is_vendor', 'is_customer', 'is_manager',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('national_id', 'phone_number')
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_vendor', 'is_customer', 'is_manager',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('national_id', 'phone_number')
        })
    )
admin.site.register(CustomUser, CustomUserAdmin)

class TkeysAdmin(admin.ModelAdmin):
    list_display = ('u_name', 'u_key')

admin.site.register(Tkeys, TkeysAdmin)

class CompanyMetaAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'protocol', 'phone', 'updated_at', 'created_at')

admin.site.register(CompanyMeta, CompanyMetaAdmin)