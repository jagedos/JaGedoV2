from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from management.models import Counties, PickUps
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
  
  counties =  Counties.objects.filter(status=True)
  points =  PickUps.objects.all()
  template = loader.get_template('settings/pickup.html')
  context = {
    'counties': counties,
    'points': points,
  }
  return HttpResponse(template.render(context, request))

def addrecord(request):
  x = request.POST['name']
  y = request.POST['status']
  z = request.POST['county']
  
  county = Counties.objects.get(id=z)

  member = PickUps(county=county,name=x,status=y)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def edita(request, id):
  mymember = model_to_dict(PickUps.objects.get(id=id))
  
  
  response = mymember

  return JsonResponse(response, safe=False)

def updaterecord(request):
  z = request.POST['county']
  name = request.POST['name']
  status = request.POST['status']
  id = request.POST['hidden_id']

  county = Counties.objects.get(id=z)
  
  member = PickUps.objects.get(id=id)
  member.county = county
  member.name = name
  member.status = status
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def delete(request, id):
  member = PickUps.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)