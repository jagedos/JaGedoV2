from django.db import models
from items.models import Products
from management.models import Counties
from accounts.models import CustomUser

# Create your models here.


class Shops(models.Model):
    name = models.CharField(default="None", max_length=255)
    county = models.ForeignKey(
        Counties, on_delete=models.SET_NULL, blank=True, null=True
    )
    vendor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, blank=True, null=True
    )
    status = models.BooleanField(default=True)
    is_fundi = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Vproducts(models.Model):
    product = models.ForeignKey(
        Products, on_delete=models.SET_NULL, blank=True, null=True
    )
    shop = models.ForeignKey(Shops, on_delete=models.SET_NULL, blank=True, null=True)
    serial = models.CharField(default="None", max_length=255)
    stock = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)
    is_fundi = models.BooleanField(default=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, blank=True, null=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
