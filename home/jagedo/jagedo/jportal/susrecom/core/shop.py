from itertools import product
from unicodedata import category
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.contrib import messages
from django.core import serializers
from items.models import Categories, Products, Pimages
from vendors.models import Vproducts,Shops
from core.models import Carts, OrderCarts, Orders
from accounts.models import CustomUser, CompanyMeta,Profile
from management.models import PickUps,Counties, LegalDocuments, LegalDocumentTypes
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils.crypto import get_random_string
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required


def index(request,uidb64):
  search=force_str(urlsafe_base64_decode(uidb64))
  current_category = uidb64
  docs = LegalDocuments.objects.filter(type__is_global=True)
  prof = Profile.objects.get(user=request.user.id)
  cats =  Categories.objects.all()
  cat = Categories.objects.all().first()
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True)
  company =  CompanyMeta.objects.get(id=1)
  
  prods =  Products.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search),status=True)
  p_sum=prods.count()
 

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  locs =  Counties.objects.filter(status=True)
  template = loader.get_template('product/shops.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'locs': locs,
    'p_sum': p_sum,
    'lid': search,
    'current_category': current_category,
    'cat': cat ,
    'cat_name': search,
    'company': company,
    'docs': docs
  }
  return HttpResponse(template.render(context, request))

@login_required
def shop_list(request,uidb64):
  search=force_str(urlsafe_base64_decode(uidb64))
  current_category = uidb64
  docs = LegalDocuments.objects.filter(type__is_global=True)
  prof = Profile.objects.get(user=request.user.id)
  cats =  Categories.objects.all()
  cat = Categories.objects.all().first()
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True)
  
  prods =  Products.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search),status=True)
  p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 8)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  locs =  Counties.objects.filter(status=True)
  template = loader.get_template('product/shop_listings.html')
  context = {
    'cats': cats,
    'cat': cat ,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'locs': locs,
    'p_sum': p_sum,
    'lid': search,
    'current_category': current_category,
    'docs': docs
  }
  return HttpResponse(template.render(context, request))




def updatelocation(request, id):
  if request.user.is_authenticated:
   loc =Counties.objects.get(id=id)
   member = Profile.objects.get(user=request.user.id)
   member.location = loc
   member.save()
  
   if id == 48:
    county = 'ALL LOCATIONS'
   else:
    county = loc.name

   response = {
        'success':'Location Updated successfully.',
        'county' : county
            }
  else:
    response = {
        'errors':'Login To Change Location !',
            }



  return JsonResponse(response)

def encrypt_id(id):
    final = urlsafe_base64_encode(force_bytes(id))
    return final
@login_required
def search(request):
  search= request.GET['search']
  prof = Profile.objects.get(user=request.user.id)
  loc = prof.location.id

  if prof.location.id == 48:
    products =  Vproducts.objects.filter(Q(product__name__icontains=search) | Q(product__category__name__icontains=search) | Q(product__brand__name__icontains=search), status=True)[:10]
  else:
    products =  Vproducts.objects.filter(Q(product__name__icontains=search) | Q(product__category__name__icontains=search) | Q(product__brand__name__icontains=search),shop__county=loc,status=True)[:10]

  res=''
  
  

  for px in products:
    id=encrypt_id(px.product.name)
    res+='<li class="list-group-item " ><a href="/product_listings/'+ str(id)+'"  > '+str(px.product.name)+' | <b>Category: </b>'+str(px.product.category)+' | <b>Brand: </b>'+str(px.product.brand)+'</a></li>'

  parameters = { 'res': res }
  response = parameters
  return JsonResponse(response)



@login_required

def allproducts(request):
  prof = Profile.objects.get(user=request.user.id)
  cats =  Categories.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True)
  if prof.location.id == 48:
    prods =  Vproducts.objects.filter(status=True)
    p_sum=prods.count()
  else:
    prods =  Vproducts.objects.filter(shop__county=prof.location.id,status=True)
    p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  locs =  Counties.objects.filter(status=True)
  template = loader.get_template('product/allproducts.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'locs': locs,
    'p_sum': p_sum,
    'docs': docs
    
  }
  return HttpResponse(template.render(context, request))


@login_required


def allproductslists(request):
  prof = Profile.objects.get(user=request.user.id)
  cats =  Categories.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True)
  if prof.location.id == 48:
    prods =  Vproducts.objects.filter(status=True)
    p_sum=prods.count()
  else:
    prods =  Vproducts.objects.filter(shop__county=prof.location.id,status=True)
    p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  locs =  Counties.objects.filter(status=True)
  template = loader.get_template('product/allproducts_lists.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'locs': locs,
    'p_sum': p_sum,
    'docs': docs
    
  }
  return HttpResponse(template.render(context, request))


@login_required


def alldiscounts(request):
  prof = Profile.objects.get(user=request.user.id)
  cats =  Categories.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True)
  if prof.location.id == 48:
    prods =  Vproducts.objects.filter(discount__gt=0,status=True)
    p_sum=prods.count()
  else:
    prods =  Vproducts.objects.filter(discount__gt=0,shop__county=prof.location.id,status=True)
    p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  locs =  Counties.objects.filter(status=True)
  template = loader.get_template('product/alldiscounts.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'locs': locs,
    'p_sum': p_sum,
    'docs': docs
    
  }
  return HttpResponse(template.render(context, request))


@login_required


def alldiscountslists(request):
  prof = Profile.objects.get(user=request.user.id)
  cats =  Categories.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True)
  if prof.location.id == 48:
    prods =  Vproducts.objects.filter(discount__gt=0,status=True)
    p_sum=prods.count()
  else:
    prods =  Vproducts.objects.filter(discount__gt=0,shop__county=prof.location.id,status=True)
    p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  locs =  Counties.objects.filter(status=True)
  template = loader.get_template('product/alldiscounts_lists.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'locs': locs,
    'p_sum': p_sum,
    'docs': docs
    
  }
  return HttpResponse(template.render(context, request))

