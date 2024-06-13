from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products
from core.models import OrderCarts, Orders, Reviews, Responses, WishList
from accounts.models import CompanyMeta,CustomUser
from vendors.models import Vproducts,Shops
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
@customer_watch

def index(request):
  active = Orders.objects.filter(customer=request.user.id).exclude(status=2).count()
  dispatched = Orders.objects.filter(customer=request.user.id,status=1).count()
  completed = Orders.objects.filter(customer=request.user.id,status=2).count()
  template = loader.get_template('cmains.html')
  context = {
    'active': active,
    'dispatched': dispatched,
    'completed': completed,
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch
def active_orders(request):
  title='Active'
  active = Orders.objects.filter(customer=request.user.id).exclude(status=2).count()
  dispatched = Orders.objects.filter(customer=request.user.id,status=1).count()
  completed = Orders.objects.filter(customer=request.user.id,status=2).count()
  acts = Orders.objects.filter(customer=request.user.id).exclude(status=2).order_by('-id')
  page = request.GET.get('page', 1)

  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('orders.html')
  context = {
    'active': active,
    'actives': actives,
    'dispatched': dispatched,
    'completed': completed,
    'title': title,
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch
def closed_orders(request):
  title='Fulfilled'
  active = Orders.objects.filter(customer=request.user.id).exclude(status=2).count()
  dispatched = Orders.objects.filter(customer=request.user.id,status=1).count()
  completed = Orders.objects.filter(customer=request.user.id,status=2).count()
  acts = Orders.objects.filter(customer=request.user.id,status=2).order_by('-id')
  page = request.GET.get('page', 1)
  
  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('orders.html')
  context = {
    'active': active,
    'actives': actives,
    'dispatched': dispatched,
    'completed': completed,
    'title': title,
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch
def reviews(request):
  title='Pending_Reviews'
  active = Orders.objects.filter(customer=request.user.id).exclude(status=2).count()
  dispatched = Orders.objects.filter(customer=request.user.id,status=1).count()
  completed = Orders.objects.filter(customer=request.user.id,status=2).count()
  checks =Orders.objects.filter(customer=request.user.id,status=2)
  serials=checks.values_list('serial', flat=True)
  acts = OrderCarts.objects.filter(serial__in=serials,is_reviewed=False).order_by('is_reviewed')
  page = request.GET.get('page', 1)
  
  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('reviews.html')
  context = {
    'active': active,
    'actives': actives,
    'dispatched': dispatched,
    'completed': completed,
    'title': title,
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch
def allreviews(request):
  title='All_Reviews'
  active = Orders.objects.filter(customer=request.user.id).exclude(status=2).count()
  dispatched = Orders.objects.filter(customer=request.user.id,status=1).count()
  completed = Orders.objects.filter(customer=request.user.id,status=2).count()
  checks =Orders.objects.filter(customer=request.user.id,status=2)
  serials=checks.values_list('serial', flat=True)
  acts = OrderCarts.objects.filter(serial__in=serials).order_by('is_reviewed')
  page = request.GET.get('page', 1)
  
  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('reviews.html')
  context = {
    'active': active,
    'actives': actives,
    'dispatched': dispatched,
    'completed': completed,
    'title': title,
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch
def profile(request):
  active = Orders.objects.filter(customer=request.user.id).exclude(status=2).count()
  dispatched = Orders.objects.filter(customer=request.user.id,status=1).count()
  completed = Orders.objects.filter(customer=request.user.id,status=2).count()
  template = loader.get_template('profile.html')
  context = {
    'active': active,
    'dispatched': dispatched,
    'completed': completed,
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch
def updaterecord(request):
 if request.method =='POST':
    first = request.POST['first_name']
    last = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    nid = request.POST['national_id']
    id = request.user.id

    
    

    echeck = CustomUser.objects.get(id=id)
    stat= echeck.is_active
    passw = echeck.password
    

    
    member = CustomUser.objects.get(id=id)
    member.first_name = first
    member.last_name = last
    member.email = email
    member.phone_number = phone
    member.national_id = nid
    member.save()

    
    

    response = {
        'success':'Data Updated successfully.' 
            }
      
 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)



@login_required
@customer_watch
def edita(request, id):
  dicta = OrderCarts.objects.get(id=id)
  ord = Orders.objects.get(serial=dicta.serial)
  title = '<b>Add_Review For | Order :</b> '+str(ord.id)+' | '+str(dicta.vproduct.product.name)
  mymember = model_to_dict(dicta)
  
  parameters = { 'cart': mymember, 'title': title, }
  response = parameters

  return JsonResponse(response, safe=False)


def editr(request, id):
  dicta = Reviews.objects.get(id=id)

  mymember = model_to_dict(dicta)
  
  parameters = { 'cart': mymember }
  response = parameters

  return JsonResponse(response, safe=False)


@login_required
@customer_watch
def wishlist(request):
  active = Orders.objects.filter(customer=request.user.id).exclude(status=2).count()
  dispatched = Orders.objects.filter(customer=request.user.id,status=1).count()
  completed = Orders.objects.filter(customer=request.user.id,status=2).count()

  acts = WishList.objects.filter(customer=request.user.id)
  page = request.GET.get('page', 1)
  
  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('wishlist.html')
  context = {
    'active': active,
    'actives': actives,
    'dispatched': dispatched,
    'completed': completed,
    
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch

def delwish(request,id):
  if request.method =='GET':
     user = request.user.id
     prod = Vproducts.objects.get(id=id)
     customer = CustomUser.objects.get(id=user)
     
     WishList.objects.filter(vproduct=prod,customer=customer).delete()
     
     

     response = {
          'success':'Product Removed Succesfully .' 
            }
            
     return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)
