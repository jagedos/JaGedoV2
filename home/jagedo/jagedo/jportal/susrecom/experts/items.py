from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from experts.models import Pitems, Pcategories, Peimages, PartnerMeta, PartnerCerts, PartnerSkills, PartnerTimes
from accounts.models import CustomUser
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.utils.crypto import get_random_string
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch, experts_watch
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
@experts_watch

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
  items = Pitems.objects.all()
  cats =  Pcategories.objects.all().values()
  pics = Peimages.objects.all()
  
  template = loader.get_template('work/items.html')
  context = {
    'items': items,
    'cats': cats,
    'pics': pics,
  }
  return HttpResponse(template.render(context, request))

def addrecord(request):
  name = request.POST['name']
  cat = request.POST['category']
  desc = request.POST['description']
  price = request.POST['price']
  imgs = request.FILES.getlist('cover')
  
  meta = PartnerMeta.objects.get(partner=request.user.id)
  if not imgs:
      response = {
        'errors':'Kindly Upload Atleast One Image.' 
            }
  else:
   category_obj = Pcategories.objects.get(id=cat)
   exp_obj = PartnerMeta.objects.get(id=meta.pk)
  
  
   member = Pitems(name=name, category=category_obj, price=price, description=desc, expert=exp_obj)
   member.save()

  
   ptid = member.pk
   pid  = Pitems.objects.get(id=ptid)

   images = request.FILES.getlist('cover')
   for image in images:
     mem = Peimages(product=pid, cover=image )
     mem.save()

  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def edita(request, id):
  products = Pitems.objects.get(id=id)
  mymember = model_to_dict(products)

  # response = {

  #   'id': mymember.id,
  #   'name': mymember.name,
  #   'category': mymember.category,
  #   'brand': mymember.brand,
  #   'units': mymember.units,
  #   'description': mymember.description,
  # }
  pics = Peimages.objects.filter(product=id)
  ima='none'

  if not pics:
     img='<i><b>No Images Uploaded!</b></i>'
  

  else :
     
      img=' <table width="100%" class="table table-striped table-bordered dt-responsive compact nowrap"> \
  <thead> \
    <tr> \
     <th>Image</th> \
      <th>Action</th> \
        </tr> </thead>\
          <tbody> \
             '
  for pic in pics:
      img+='<tr> \
      <td><img src="/media/'+str(pic.cover)+'" width="70" class="img-thumbnail"  loading="lazy"></td> \
               <td><button type="button" name="delete" id="'+str(pic.id)+'" class="idel btn btn-xs btn-danger btn-sm">Delete</button></td> </tr>'
        
      
      

  parameters = { 'mymember': mymember, 'img': img, }
  response = parameters

  return JsonResponse(response)

def updaterecord(request):
  name = request.POST['name']
  cat = request.POST['category']
  price = request.POST['price']
  desc = request.POST['description']

  category_obj = Pcategories.objects.get(id=cat)
  

  id = request.POST['hidden_id']
  member = Pitems.objects.get(id=id)
  member.name = name
  member.category = category_obj
  member.description = desc
  member.price = price
  member.save()

  pid  = Pitems.objects.get(id=id)

  images = request.FILES.getlist('cover')
  if not images:
      x=''
  else:
    for image in images:
      mem = Peimages(product=pid, cover=image )
      mem.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def idelete(request, id):
  m = Peimages.objects.get(id=id)
  member = Peimages.objects.get(id=id)
  member.delete()
 
  pics = Peimages.objects.filter(product=m.product)
  

  if not pics:
     img='<i><b>No Images Uploaded!</b></i>'
  

  else :
     
      img=' <table width="100%" class="table table-striped table-bordered dt-responsive compact nowrap"> \
  <thead> \
    <tr> \
     <th>Image</th> \
      <th>Action</th> \
        </tr> </thead>\
          <tbody> \
             '
  for pic in pics:
      img+='<tr> \
      <td><img src="/media/'+str(pic.cover)+'" width="70" class="img-thumbnail"  loading="lazy"></td> \
               <td><button type="button" name="idel" id="'+str(pic.id)+'" class="idel btn btn-xs btn-danger btn-sm">Delete</button></td> </tr>'
        
      
      

  parameters = { 'img': img, }
  response = parameters
  return JsonResponse(response)

def delete(request, id):
  
  Peimages.objects.filter(id=id).delete()
  member = Pitems.objects.get(id=id)
  member.delete()
 
  
  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)