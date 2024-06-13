# resources.py
from import_export import resources, fields
from vendors.models import Vproducts, Shops
from import_export.instance_loaders import ModelInstanceLoader
from import_export.results import RowResult
from items.models import Products
from import_export.admin import ImportExportModelAdmin


class VproductsResource(resources.ModelResource):
    product_name = fields.Field(column_name="Product Name", attribute="product__name")
    shop_name = fields.Field(column_name="Shop Name", attribute="shop__name")

    class Meta:
        model = Vproducts
        fields = ("id", "product_name", "shop_name", "cost", "price")
        import_id_fields = ["id"]
        export_order = ("id", "product_name", "shop_name", "cost", "price")
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        product_name = row.get("Product Name")
        shop_name = row.get("Shop Name")

        if product_name:
            try:
                product = Products.objects.get(name=product_name)
                row["product"] = product.id
            except Products.DoesNotExist:
                raise Exception("Product not found: {}".format(product_name))
        else:
            row["product"] = None

        if shop_name:
            try:
                shop = Shops.objects.get(name=shop_name)
                row["shop"] = shop.id
            except Shops.DoesNotExist:
                raise Exception("Shop not found: {}".format(shop_name))
        else:
            row["shop"] = None


# create resource for import export of products
class ProductsResource(resources.ModelResource):
    class Meta:
        model = Products
        fields = ("id", "name", "price")
        import_id_fields = ["id"]
        export_order = ("id", "name", "price")
        skip_unchanged = True
        report_skipped = True
