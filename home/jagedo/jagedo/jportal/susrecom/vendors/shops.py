from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products
from vendors.models import Shops, Vproducts
from management.models import Counties
from accounts.models import CustomUser
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from accounts.decorators import (
    authentication_not_required,
    customer_watch,
    manager_watch,
    vendor_watch,
)
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
@vendor_watch
def index(request):
    shops = Shops.objects.filter(vendor=request.user.id)
    counties = Counties.objects.filter(status=True)
    template = loader.get_template("settings/shops.html")
    context = {
        "shops": shops,
        "counties": counties,
    }
    return HttpResponse(template.render(context, request))


@login_required
@vendor_watch
def addrecord(request):
    x = request.POST["name"]
    y = request.POST["county"]
    z = request.user.id

    county = Counties.objects.get(id=y)
    vendor = CustomUser.objects.get(id=z)

    member = Shops(name=x, county=county, vendor=vendor)
    member.save()

    # add all products where status is true to the shop
    products = Products.objects.filter(status=True)
    products_to_add = []
    for product in products:
        shop = Shops.objects.get(id=member.id)
        cost = 0
        price = 0
        discount = 0
        status = True
        stock = 0
        user = request.user.id
        products_to_add.append(
            Vproducts(
                product=product,
                shop=shop,
                cost=cost,
                price=price,
                discount=discount,
                status=status,
                stock=stock,
                user_id=user,
            )
        )

    Vproducts.objects.bulk_create(products_to_add)

    response = {"success": "Data Added successfully."}
    return JsonResponse(response)


@login_required
@vendor_watch
def edita(request, id):
    mymember = model_to_dict(Shops.objects.get(id=id))

    response = mymember

    return JsonResponse(response, safe=False)


def updaterecord(request):
    name = request.POST["name"]
    c = request.POST["county"]
    id = request.POST["hidden_id"]

    county = Counties.objects.get(id=c)

    member = Shops.objects.get(id=id)
    member.name = name
    member.county = county
    member.save()

    response = {"success": "Data Updated successfully."}
    return JsonResponse(response)


@login_required
@vendor_watch
def delete(request, id):
    member = Shops.objects.get(id=id)

    Vproducts.objects.filter(shop=id).delete()

    member.delete()

    response = {"success": "Data Deleted successfully."}
    return JsonResponse(response)
