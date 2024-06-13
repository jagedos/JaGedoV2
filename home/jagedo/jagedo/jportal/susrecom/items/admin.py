from django.contrib import admin
from items.models import Categories, Products, Brands, Munits, Pimages
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'created_at')
admin.site.register(Products, ProductAdmin)
class CatAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
admin.site.register(Categories, CatAdmin)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
admin.site.register(Brands, BrandAdmin)
class MunitAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
admin.site.register(Munits, MunitAdmin)
class PimageAdmin(admin.ModelAdmin):
    list_display = ('product', 'created_at')

admin.site.register(Pimages, PimageAdmin)

