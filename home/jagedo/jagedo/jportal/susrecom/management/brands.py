from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products, Brands
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
@manager_watch
def index(request):
  items = Products.objects.all().values()
  cats =  Categories.objects.all().values()
  brands =  Brands.objects.all().values()
  template = loader.get_template('items/brands.html')
  context = {
    'items': items,
    'cats': cats,
    'brands': brands,
  }
  return HttpResponse(template.render(context, request))

def addrecord(request):
  x = request.POST['name']
  
  member = Brands(name=x)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def edita(request, id):
  mymember = model_to_dict(Brands.objects.get(id=id))

  #response = {

    #'id': mymember.id,
    #'first': mymember.firstname,
    #'last': mymember.lastname,
 # }

  
  
  response = mymember

  return JsonResponse(response, safe=False)

def updaterecord(request):
  name = request.POST['name']
  id = request.POST['hidden_id']
  member = Brands.objects.get(id=id)
  member.name = name
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def delete(request, id):
  member = Brands.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)