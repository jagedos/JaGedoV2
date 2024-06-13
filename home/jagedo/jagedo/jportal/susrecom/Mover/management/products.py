from os import stat
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products, Brands, Munits, Pimages
from vendors.models import Vproducts, Shops
from accounts.models import CustomUser
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.db.models import Q, Sum, F
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.decorators import (
    authentication_not_required,
    customer_watch,
    manager_watch,
    vendor_watch,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.
# create list of products for datatable based on shop
class ProductsListJson(BaseDatatableView):
    columns = ["id", "product", "shop", "cost", "price", "cover_image"]
    search_fields = ["product__name__icontains", "shop__name__icontains"]

    def get_initial_queryset(self):
        temp = self.request.POST.get("temp")
        shop = int(self.request.POST.get("shop"))

        if temp == "v":
            if shop == 0:
                queryset = Vproducts.objects.all()
            else:
                queryset = Vproducts.objects.filter(shop__vendor=shop)

        else:
            if shop == 0:
                queryset = Vproducts.objects.all()
            else:
                queryset = Vproducts.objects.filter(shop=shop)

        return queryset

    def filter_queryset(self, qs):
        search = self.request.POST.get("search[value]", None)
        if search:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{field: search})
            qs = qs.filter(query)
        return qs

    def render_column(self, row, column):
        if column == "cover_image":
            pi = Pimages.objects.filter(product=row.product.id)
            if pi.exists():
                pic = pi.first()
                final = (
                    '<img src="/media/'
                    + str(pic.cover)
                    + '" class="img-thumbnail" width="100" loading="lazy">'
                )
            else:
                final = "No_Image"
            return final
        else:
            return super(ProductsListJson, self).render_column(row, column)


@login_required
@manager_watch
def index(request):
    if request.method == "GET":
        tem = int(request.GET["shop"])
        if tem > 0:
            id = tem
            ishop = Shops.objects.get(id=id)
            shop = ishop.name
            mshop = id

        else:
            shop = "All_Locations"
            mshop = 0

        items = Products.objects.filter(status=True)
        dukas = Shops.objects.all()

        template = loader.get_template("vendors/products.html")
        context = {
            "items": items,
            "shop": shop,
            "temp": "s",
            "dukas": dukas,
            "mshop": mshop,
        }
        return HttpResponse(template.render(context, request))
    else:
        messages.success(request, "Invalid Request !")
        return redirect("/mans/vproducts/")


@login_required
@manager_watch
def vindex(request):
    if request.method == "GET":
        tem = int(request.GET["shop"])

        if tem > 0:
            id = tem
            cs = CustomUser.objects.get(id=tem)
            shop = cs.first_name + " " + cs.last_name + "| Products"
            vendorid = tem

        else:
            shop = "All_Vendors| Products"
            vendorid = 0

        items = Products.objects.filter(status=True)
        dukas = Shops.objects.all()

        template = loader.get_template("vendors/products.html")
        context = {
            "items": items,
            "vendorid": vendorid,
            "shop": shop,
            "temp": "v",
            "dukas": dukas,
        }
        return HttpResponse(template.render(context, request))
    else:
        messages.success(request, "Invalid Request !")
        return redirect("/mans/vvproducts/")


@login_required
@manager_watch
def product_filter(request):
    shops = Shops.objects.filter(status=True)

    template = loader.get_template("vendors/product_shop_filter.html")
    context = {
        "shops": shops,
    }
    return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def vendor_filter(request):
    shops = CustomUser.objects.filter(is_vendor=True, is_active=True)

    template = loader.get_template("vendors/product_vendor_filter.html")
    context = {
        "shops": shops,
    }
    return HttpResponse(template.render(context, request))


def addrecord(request):
    if request.method == "POST":
        x = request.POST["product"]
        y = request.POST["shop"]
        stock = int(request.POST["stock"])
        price = request.POST["price"]
        status = request.POST["status"]
        discount = int(request.POST["discount"])
        z = request.user.id

        check = Vproducts.objects.filter(shop=y, product=x)
        if check.exists():
            response = {"errors": "This Products Already Exists In This Shop!"}
            return JsonResponse(response)

        else:
            product = Products.objects.get(id=x)
            shop = Shops.objects.get(id=y)
            user = CustomUser.objects.get(id=z)

            member = Vproducts(
                product=product,
                shop=shop,
                price=price,
                discount=discount,
                status=status,
                stock=stock,
                user=user,
            )
            member.save()
            response = {"success": "Product Added successfully."}
            return JsonResponse(response)
    else:
        response = {"errors": "Invalid Request!"}
        return JsonResponse(response)


@login_required
@manager_watch
def edita(request, id):
    mymember = model_to_dict(Vproducts.objects.get(id=id))

    response = mymember

    return JsonResponse(response, safe=False)


def updaterecord(request):
    x = request.POST["product"]
    stock = int(request.POST["stock"])
    price = int(request.POST["price"])
    status = request.POST["status"]
    discount = request.POST["discount"]

    product = Products.objects.get(id=x)

    id = request.POST["hidden_id"]

    member = Vproducts.objects.get(id=id)
    member.product = product
    member.stock = stock
    member.price = price
    member.status = status
    member.discount = discount
    member.save()

    response = {"success": "Data Updated successfully."}
    return JsonResponse(response)


@login_required
@manager_watch
def delete(request, id):
    member = Vproducts.objects.get(id=id)
    member.delete()

    response = {"success": "Data Deleted successfully."}
    return JsonResponse(response)
