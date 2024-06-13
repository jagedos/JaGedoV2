from django.shortcuts import render
from django_datatables_view.base_datatable_view import BaseDatatableView
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
class CatDataTableView(BaseDatatableView):
    model = Categories
    columns = ['name', 'expert','slide']


class PcatDataTableView(BaseDatatableView):
    columns = ['name']
    search_fields = ['name__icontains']

    def get_initial_queryset(self):
        pid = self.request.POST.get("pid")
        qset = Products.objects.filter(category=pid,status=True)
        return qset

    def filter_queryset(self, qss):
        search = self.request.POST.get(u'search[value]', None)
        if search:
            qss = qss.filter(**{f'{self.search_fields[0]}': search})
        return qss

@login_required
@manager_watch
def index(request):
  items = Products.objects.all().values()
  cats =  Categories.objects.all().values()
  brands =  Brands.objects.all().values()
  template = loader.get_template('items/categories.html')
  context = {
    'items': items,
    'cats': cats,
    'brands': brands,
  }
  return HttpResponse(template.render(context, request))

def catitems(request,id):
  checki= Categories.objects.get(id=id)
  pid=checki.pk
  template = loader.get_template('items/catitems.html')
  context = {
    'pid': pid,
    'q': checki,

    
  }
  return HttpResponse(template.render(context, request))



def addrecord(request):
  x = request.POST['name']
  y = request.POST['section']
  z = request.POST['slide']
  
  member = Categories(name=x,expert=y,slide=z)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def edita(request, id):
  mymember = model_to_dict(Categories.objects.get(id=id))

  #response = {

    #'id': mymember.id,
    #'first': mymember.firstname,
    #'last': mymember.lastname,
 # }

  
  
  response = mymember

  return JsonResponse(response, safe=False)

def updaterecord(request):
  name = request.POST['name']
  y = request.POST['section']
  z = request.POST['slide']

  id = request.POST['hidden_id']
  member = Categories.objects.get(id=id)
  member.name = name
  member.expert=y
  member.slide= z
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def delete(request, id):
  member = Categories.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)


def changestat(request, id):
  member = Products.objects.filter(id=id)
  prod=member.first()
  if (prod.slide):
    member.update(slide=False)
  else:
     member.update(slide=True)


  response = {
        'success':'Status Adjusted successfully.' 
            }
  return JsonResponse(response)