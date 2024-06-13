from django_datatables_view.base_datatable_view import BaseDatatableView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products, Brands, Munits, Pimages
from vendors.models import Shops, Vproducts
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json, datetime
from django.db.models import Q, F, Count, Sum, Avg
from vendors.resources import ProductsResource
from math import ceil
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.utils.crypto import get_random_string
from accounts.decorators import (
    authentication_not_required,
    customer_watch,
    manager_watch,
    vendor_watch,
)
from django.contrib.auth.decorators import login_required
from import_export.formats import base_formats
from tablib import Dataset
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
class ProdDataTableView(BaseDatatableView):
    columns = ["name", "category", "brand", "units", "status"]
    search_fields = [
        "name__icontains",
        "category__name__icontains",
        "brand__name__icontains",
    ]

    def get_initial_queryset(self):
        queryset = Products.objects.all()
        return queryset

    def filter_queryset(self, qs):
        search = self.request.POST.get("search[value]", None)
        if search:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{field: search})
            qs = qs.filter(query)
        return qs


@login_required
@manager_watch
class CustomEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, ImageFieldFile):
            return 0

            # Do whatever appropriate for your case, like returning None
        return super(CustomEncoder, self).default(obj)


# def dictfetchall(cursor):
#     "Return all rows from a cursor as a dict"
#     columns = [col[0] for col in cursor.description]
#     return [
#         dict(zip(columns, row))
#         for row in cursor.fetchall()
#     ]


# def index(request):
#   cursor = connection.cursor()
#   cursor.execute("SELECT items_products.id , items_products.name , items_categories.name AS catname, items_brands.name AS bname FROM items_products \
#    INNER JOIN items_categories ON items_products.category = items_categories.id \
#    INNER JOIN items_brands ON items_products.brand = items_brands.id   ")
#   items = dictfetchall(cursor)

#   cats =  Categories.objects.all().values()
#   brands =  Brands.objects.all().values()
#   template = loader.get_template('items/items.html')
#   context = {
#     'items': items,
#     'cats': cats,
#     'brands': brands,
#   }
#   return HttpResponse(template.render(context, request))


def index(request):
    items = Products.objects.all()
    cats = Categories.objects.all().values()
    brands = Brands.objects.all().values()
    units = Munits.objects.all().values()
    pics = Pimages.objects.all()

    template = loader.get_template("items/items.html")
    context = {
        "items": items,
        "cats": cats,
        "brands": brands,
        "units": units,
        "pics": pics,
    }
    return HttpResponse(template.render(context, request))


def addrecord(request):
    name = request.POST["name"]
    cat = request.POST["category"]
    brand = request.POST["brand"]
    desc = request.POST["description"]
    unit = request.POST["units"]
    weight = request.POST["weight"]
    price = request.POST["price"]

    u_id = get_random_string(length=10)

    category_obj = Categories.objects.get(id=cat)
    brand_obj = Brands.objects.get(id=brand)
    unit_obj = Munits.objects.get(id=unit)

    member = Products(
        name=name,
        category=category_obj,
        serial=u_id,
        brand=brand_obj,
        units=unit_obj,
        description=desc,
        weight=weight,
        price=price,
    )
    member.save()

    p_obj = Products.objects.get(serial=u_id)
    ptid = p_obj.id
    pid = Products.objects.get(id=ptid)

    images = request.FILES.getlist("cover")
    for image in images:
        mem = Pimages(product=pid, cover=image)
        mem.save()

    # add product to all vendors by appending in a single query
    # get all vendors
    vendors = Shops.objects.all()
    for vendor in vendors:
        v_obj = Vproducts(shop=vendor, product=pid, price=price)
        v_obj.save()

    response = {"success": "Data Added successfully."}
    return JsonResponse(response)


def edita(request, id):
    products = Products.objects.get(id=id)
    mymember = model_to_dict(products)

    # get average price from vendor products using avg function
    vproducts = Vproducts.objects.filter(product=id).aggregate(Avg("price"))
    # assign average price to mymember to two decimal places
    mymember["vprice"] = round(vproducts["price__avg"], 2)

    # get all images for product

    pics = Pimages.objects.filter(product=id)
    ima = "none"

    if not pics:
        img = "<i><b>No Images Uploaded!</b></i>"

    else:
        img = ' <table width="100%" class="table table-striped table-bordered dt-responsive compact nowrap"> \
  <thead> \
    <tr> \
     <th>Image</th> \
      <th>Action</th> \
        </tr> </thead>\
          <tbody> \
             '
    for pic in pics:
        img += (
            '<tr> \
      <td><img src="/media/'
            + str(pic.cover)
            + '" width="70" class="img-thumbnail"  loading="lazy"></td> \
               <td><button type="button" name="delete" id="'
            + str(pic.id)
            + '" class="idel btn btn-xs btn-danger btn-sm">Delete</button></td> </tr>'
        )

    parameters = {
        "mymember": mymember,
        "img": img,
    }
    response = parameters

    return JsonResponse(response)


def updaterecord(request):
    name = request.POST["name"]
    desc = request.POST["description"]
    cat = request.POST["category"]
    brand = request.POST["brand"]
    unit = request.POST["units"]
    weight = request.POST["weight"]
    price = request.POST["price"]
    average_price = request.POST["average_price"]

    category_obj = Categories.objects.get(id=cat)
    brand_obj = Brands.objects.get(id=brand)
    unit_obj = Munits.objects.get(id=unit)

    id = request.POST["hidden_id"]
    member = Products.objects.get(id=id)
    member.name = name
    member.category = category_obj
    member.brand = brand_obj
    member.units = unit_obj
    member.description = desc
    member.weight = weight
    if "use_average_price" in request.POST and request.POST["use_average_price"] == "1":
        member.price = average_price
    else:
        member.price = price

    member.save()

    pid = Products.objects.get(id=id)

    images = request.FILES.getlist("cover")
    for image in images:
        mem = Pimages(product=pid, cover=image)
        mem.save()

    response = {"success": "Data Updated successfully."}
    return JsonResponse(response)


def idelete(request, id):
    m = Pimages.objects.get(id=id)
    member = Pimages.objects.get(id=id)
    member.delete()

    pics = Pimages.objects.filter(product=m.product)

    if not pics:
        img = "<i><b>No Images Uploaded!</b></i>"

    else:
        img = ' <table width="100%" class="table table-striped table-bordered dt-responsive compact nowrap"> \
  <thead> \
    <tr> \
     <th>Image</th> \
      <th>Action</th> \
        </tr> </thead>\
          <tbody> \
             '
    for pic in pics:
        img += (
            '<tr> \
      <td><img src="/media/'
            + str(pic.cover)
            + '" width="70" class="img-thumbnail"  loading="lazy"></td> \
               <td><button type="button" name="idel" id="'
            + str(pic.id)
            + '" class="idel btn btn-xs btn-danger btn-sm">Delete</button></td> </tr>'
        )

    parameters = {
        "img": img,
    }
    response = parameters
    return JsonResponse(response)


def delete(request, id):
    dets = CustomUser.objects.get(id=id)
    user_type = dets.usertype.pk
    if user_type == 1:
        # delete all vendor products for this product
        Vproducts.objects.filter(product=id).delete()

        member = Products.objects.get(id=id)
        member.delete()

        response = {"success": "Data Deleted successfully."}
    else:
        response = {"errors": "Only vendors can be deleted."}

    return JsonResponse(response)


# create function to update all product prices using average price from vendor products, update all prices in a single query
def update_all_prices(request):
    products = Products.objects.all()
    for product in products:
        vproducts = Vproducts.objects.filter(product=product.pk).aggregate(Avg("price"))
        product.price = round(vproducts["price__avg"], 2)
        product.save()

    response = {"success": "All prices updated successfully."}
    return JsonResponse(response)


def export_products(request):
    products_resource = ProductsResource()
    dataset = products_resource.export()
    xlsx_format = base_formats.XLSX()  # Instantiate the XLSX format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    response = HttpResponse(dataset.xlsx, content_type=xlsx_format.CONTENT_TYPE)
    response[
        "Content-Disposition"
    ] = f'attachment; filename="Jagedo_PML_{timestamp}.xlsx"'
    return response


@csrf_exempt
def upload_products(request):
    if request.method == "POST":
        products_resource = ProductsResource()
        dataset = Dataset().load(request.FILES["file"].read(), format="xlsx")
        result = products_resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            products_resource.import_data(dataset, dry_run=False)
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
