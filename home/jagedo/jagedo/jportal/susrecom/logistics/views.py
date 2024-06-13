from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from core.models import OrderCarts,Orders
from items.models import Categories, Products
from django.forms.models import model_to_dict
from accounts.models import CustomUser
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.db.models import Sum, Count
from accounts.decorators import authentication_not_required, customer_watch, manager_watch,logistics_watch
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
@logistics_watch
def index(request):
  template = loader.get_template('logsmains.html')
  context = {
    'products': 1,
  }
  return HttpResponse(template.render(context, request))
