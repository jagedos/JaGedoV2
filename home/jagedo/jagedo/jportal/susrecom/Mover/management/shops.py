from django.shortcuts import render, redirect
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
from django.contrib import messages
from django.contrib.auth.views import LoginView
import json, datetime
from accounts.decorators import (
    authentication_not_required,
    customer_watch,
    manager_watch,
    vendor_watch,
)
from django.contrib.auth.decorators import login_required
from vendors.resources import VproductsResource
from import_export.formats import base_formats
from tablib import Dataset
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@login_required
@manager_watch
def filter(request):
    vendors = CustomUser.objects.filter(is_vendor=True)
    template = loader.get_template("vendors/filter.html")
    context = {
        "vendors": vendors,
    }
    return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def index(request):
    if request.method == "GET":
        v = int(request.GET["vendor"])
        if v == 0:
            vname = "All_Vendors"
            shops = Shops.objects.all()
        else:
            vl = CustomUser.objects.get(id=v)
            vname = vl.first_name + " " + vl.last_name
            shops = Shops.objects.filter(vendor=v)

        vendors = CustomUser.objects.filter(is_vendor=True)
        counties = Counties.objects.filter(status=True)
        template = loader.get_template("vendors/shops.html")
        context = {
            "shops": shops,
            "vendors": vendors,
            "vname": vname,
            "v": v,
            "counties": counties,
        }
        return HttpResponse(template.render(context, request))
    else:
        messages.success(request, "Invalid Request !")
        return redirect("/mans/vshops/")


@login_required
@manager_watch
def addrecord(request):
    x = request.POST["name"]
    y = request.POST["county"]
    z = request.POST["vendor"]

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
@manager_watch
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
@manager_watch
def delete(request, id):
    member = Shops.objects.get(id=id)

    Vproducts.objects.filter(shop=id).delete()

    member.delete()

    response = {"success": "Data Deleted successfully."}
    return JsonResponse(response)


@login_required
@manager_watch
def status(request, id):
    member = Shops.objects.get(id=id)
    if member.status:
        stat = False
    else:
        stat = True

    update = Shops.objects.get(id=id)
    update.status = stat
    update.save()

    response = {"success": "Data Deleted successfully."}
    return JsonResponse(response)


def export_vproducts(request, id):
    vproducts_resource = VproductsResource()
    queryset = Vproducts.objects.filter(shop_id=id)
    dataset = vproducts_resource.export(queryset)
    xlsx_format = base_formats.XLSX()  # Instantiate the XLSX format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    response = HttpResponse(dataset.xlsx, content_type=xlsx_format.CONTENT_TYPE)
    response[
        "Content-Disposition"
    ] = f'attachment; filename="Jagedo_Products_List_{timestamp}.xlsx"'
    return response


def export_vendor_products(request, id):
    vproducts_resource = VproductsResource()
    queryset = Vproducts.objects.filter(shop__vendor=id)
    dataset = vproducts_resource.export(queryset)
    xlsx_format = base_formats.XLSX()  # Instantiate the XLSX format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    response = HttpResponse(dataset.xlsx, content_type=xlsx_format.CONTENT_TYPE)
    response[
        "Content-Disposition"
    ] = f'attachment; filename="Jagedo_Products_List_{timestamp}.xlsx"'
    return response


@csrf_exempt
def upload_vproducts(request):
    if request.method == "POST":
        vproducts_resource = VproductsResource()
        dataset = Dataset().load(request.FILES["file"].read(), format="xlsx")
        result = vproducts_resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            vproducts_resource.import_data(dataset, dry_run=False)
            return JsonResponse({"success": "Data uploaded successfully"})
        else:
            errors = []
            for row in result.row_errors():
                errors.append(
                    f"Row {row[0] + 1}: {', '.join([str(e.error) for e in row[1]])}"
                )

            print(errors)
            return JsonResponse(
                {
                    "error": f"Data upload failed. {len(errors)} row(s) with errors: {', '.join(errors)}"
                },
                status=400,
            )
    return JsonResponse({"error": "Invalid request"}, status=400)
