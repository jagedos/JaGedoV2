from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products
from accounts.models import CompanyMeta, CustomUser
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json, africastalking, re
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required
from accounts.models import Tkeys

# Create your views here.
@login_required
@manager_watch
def index(request):
  items = Products.objects.all().values()
  cats =  Categories.objects.all().values()
  
  items = Tkeys.objects.get()
  username =  items.u_name
  api_key =  items.u_key

  
  africastalking.initialize(username, api_key)

  # Get the user data, which includes the credit balance
  application = africastalking.Application

  bal = application.fetch_application_data()
  # Check the credit balance
  balance_string = bal["UserData"]["balance"]
  balance= balance_string.split(" ")[1] 


  template = loader.get_template('mains.html')
  context = {
    'items': items,
    'cats': cats,
    'balance': balance,
    'username': username,
  }
  return HttpResponse(template.render(context, request))


def metrics(request):
    customers = CustomUser.objects.filter(is_customer=True, is_active=True).count()
    vendors = CustomUser.objects.filter(is_vendor=True, is_active=True).count()
    managers = CustomUser.objects.filter(is_manager=True, is_active=True).count()
    partners = CustomUser.objects.filter(is_expert=True, is_active=True).count()
    vpartners = CustomUser.objects.filter(
        is_expert=True, is_approved=True, is_active=True
    ).count()
    uvpartners = CustomUser.objects.filter(
        is_expert=True, is_approved=False, is_active=True
    ).count()
    inactive = CustomUser.objects.filter(is_active=False).count()
    total = CustomUser.objects.all().count()

    custavg = int(customers / total * 100)
    vendavg = int(vendors / total * 100)
    manavg = int(managers / total * 100)
    inactavg = int(inactive / total * 100)
    partavg = int(partners / total * 100)
    vpartavg = int(vpartners / total * 100)
    uvpartavg = int(uvpartners / total * 100)

    parameters = {
        "cavg": custavg,
        "vavg": vendavg,
        "mavg": manavg,
        "iavg": inactavg,
        "pavg": partavg,
        "vpavg": vpartavg,
        "uvpavg": uvpartavg,
    }

    response = parameters

    return JsonResponse(response)