from django.contrib import admin
from vendors.models import Vproducts, Shops
from import_export.admin import ImportExportModelAdmin
from vendors.resources import VproductsResource


class ShopsAdmin(admin.ModelAdmin):
    list_display = ("name", "county", "vendor", "updated_at", "created_at")


admin.site.register(Shops, ShopsAdmin)


class VproductsAdmin(ImportExportModelAdmin):
    resource_class = VproductsResource
    list_display = (
        "product",
        "shop",
        "stock",
        "cost",
        "price",
        "discount",
        "status",
        "user",
        "updated_at",
        "created_at",
    )


# Ensure to unregister the previous registration before registering again

admin.site.register(Vproducts, VproductsAdmin)
