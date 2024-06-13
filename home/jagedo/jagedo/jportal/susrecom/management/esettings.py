from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from experts.models import Fields, Skills, Certs, Wdays, Pcategories
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
  fields =  Fields.objects.all().values()
  template = loader.get_template('experts/fields.html')
  context = {
    
    'fields': fields,
  }
  return HttpResponse(template.render(context, request))

def addrecord(request):
  x = request.POST['name']
  
  member = Fields(name=x)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def edita(request, id):
  mymember = model_to_dict(Fields.objects.get(id=id))

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
  member = Fields.objects.get(id=id)
  member.name = name
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def delete(request, id):
  member = Fields.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)


@login_required
@manager_watch
def sindex(request):
  fields =  Fields.objects.all().values()
  skills =  Skills.objects.all().order_by('field')
  template = loader.get_template('experts/skills.html')
  context = {
    
    'fields': fields,
    'skills': skills,
  }
  return HttpResponse(template.render(context, request))


def saddrecord(request):
  x = request.POST['name']
  y = request.POST['field']

  field = Fields.objects.get(id=y)
  member = Skills(name=x,field=field)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def sedita(request, id):
  mymember = model_to_dict(Skills.objects.get(id=id))

  #response = {

    #'id': mymember.id,
    #'first': mymember.firstname,
    #'last': mymember.lastname,
 # }

  
  
  response = mymember

  return JsonResponse(response, safe=False)

def supdaterecord(request):
  name = request.POST['name']
  y = request.POST['field']

  field = Fields.objects.get(id=y)

  id = request.POST['hidden_id']
  member = Skills.objects.get(id=id)
  member.name = name
  member.field = field
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def sdelete(request, id):
  member = Skills.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)




@login_required
@manager_watch
def cindex(request):
  fields =  Certs.objects.all().values()
  template = loader.get_template('experts/certs.html')
  context = {
    
    'fields': fields,
  }
  return HttpResponse(template.render(context, request))

def caddrecord(request):
  x = request.POST['name']
  
  member = Certs(name=x)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def cedita(request, id):
  mymember = model_to_dict(Certs.objects.get(id=id))

  response = mymember

  return JsonResponse(response, safe=False)

def cupdaterecord(request):
  name = request.POST['name']
  id = request.POST['hidden_id']
  member = Certs.objects.get(id=id)
  member.name = name
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def cdelete(request, id):
  member = Certs.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)

@login_required
@manager_watch
def wdindex(request):
  fields =  Wdays.objects.all()
  template = loader.get_template('experts/days.html')
  context = {
    
    'fields': fields,
  }
  return HttpResponse(template.render(context, request))

def wdaddrecord(request):
  x = request.POST['name']
  y = int(request.POST['status'])

  if y == 0:
      stat=False
  else:
      stat=True
  
  member = Wdays(name=x,status=stat)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def wdedita(request, id):
  mymember = model_to_dict(Wdays.objects.get(id=id))

  response = mymember

  return JsonResponse(response, safe=False)

def wdupdaterecord(request):
  name = request.POST['name']
  y = int(request.POST['status'])

  if y == 0:
      stat=False
  else:
      stat=True
      
  id = request.POST['hidden_id']
  member = Wdays.objects.get(id=id)
  member.name = name
  member.status = stat
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def wddelete(request, id):
  member = Wdays.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)




@login_required
@manager_watch
def ecindex(request):
  fields =  Pcategories.objects.all().values()
  template = loader.get_template('experts/cats.html')
  context = {
    
    'cats': fields,
  }
  return HttpResponse(template.render(context, request))

def ecaddrecord(request):
  x = request.POST['name']
  
  member = Pcategories(name=x)
  member.save()
  response = {
        'success':'Data Added successfully.' 
            }
  return JsonResponse(response)

def ecedita(request, id):
  mymember = model_to_dict(Pcategories.objects.get(id=id))

  #response = {

    #'id': mymember.id,
    #'first': mymember.firstname,
    #'last': mymember.lastname,
 # }

  
  
  response = mymember

  return JsonResponse(response, safe=False)

def ecupdaterecord(request):
  name = request.POST['name']
  id = request.POST['hidden_id']
  member = Pcategories.objects.get(id=id)
  member.name = name
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def ecdelete(request, id):
  member = Pcategories.objects.get(id=id)
  member.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)
