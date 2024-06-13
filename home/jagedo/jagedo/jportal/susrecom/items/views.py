from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
  items = Products.objects.all().values()
  cats =  Categories.objects.all().values()
  template = loader.get_template('vproducts.html')
  context = {
    'items': items,
    'cats': cats,
  }
  return HttpResponse(template.render(context, request))

def shops(request):
  items = Products.objects.all().values()
  cats =  Categories.objects.all().values()
  template = loader.get_template('products.html')
  context = {
    'items': items,
    'cats': cats,
  }
  return HttpResponse(template.render(context, request))

def addrecord(request):
  x = request.POST['first']
  y = request.POST['last']
  member = Members(firstname=x, lastname=y)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def edita(request, id):
  mymember = model_to_dict(Members.objects.get(id=id))

  #response = {

    #'id': mymember.id,
    #'first': mymember.firstname,
    #'last': mymember.lastname,
 # }

  
  
  response = mymember

  return JsonResponse(response, safe=False)

def updaterecord(request):
  first = request.POST['first']
  last = request.POST['last']
  id = request.POST['hidden_id']
  member = Members.objects.get(id=id)
  member.firstname = first
  member.lastname = last
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def delete(request, id):
  member = Members.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)