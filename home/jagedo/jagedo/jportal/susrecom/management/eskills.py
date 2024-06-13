from django.shortcuts import render
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products, Brands
from experts.models import ExpertCats,ExpertSkills
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required

# Create your views here.
class EskillsDataTableView(BaseDatatableView):
    columns = ['category','name', 'status']

    def get_initial_queryset(self):
        qset = ExpertSkills.objects.order_by('category')
        return qset


@login_required
@manager_watch
def index(request):
  
  brands =  ExpertCats.objects.all()
  template = loader.get_template('experts/lists/skills.html')
  context = {
    'brands': brands,
  }
  return HttpResponse(template.render(context, request))




def addrecord(request):
  q = request.FILES['cover']
  x = request.POST['name']
  y = request.POST['category']
  z = request.POST['status']

  cat=ExpertCats.objects.get(id=y)
  
  member = ExpertSkills(category=cat,name=x,cover=q,status=z)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def edita(request, id):
  products = ExpertSkills.objects.get(id=id)

  parameters = { 'id': products.pk,
                 'name': products.name,
                 'category': products.category.pk,
                 'cover': str(products.cover),
                 'status': products.status,
                 

   }
  response = parameters

  return JsonResponse(response, safe=False)

def updaterecord(request):
  x = request.POST['name']
  
  y = request.POST['category']
  z = request.POST['status']

  cat=ExpertCats.objects.get(id=y)

  icv = request.FILES.get('cover')
  if icv is None:
      q = 1
  else:
      q = request.FILES['cover']

  id = request.POST['hidden_id']
  member = ExpertSkills.objects.get(id=id)
  member.category=cat
  member.name = x
  if not q == 1:
      member.cover=q
  member.status= z
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def delete(request, id):
  member = ExpertSkills.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)