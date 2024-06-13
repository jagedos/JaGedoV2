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
  cats =  Categories.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True).exclude(id=search)
  current =  Shops.objects.get(id=search)
  
  prods =  Vproducts.objects.filter(Q(shop__id__iexact=search),status=True)
  p_sum=prods.count()
  
  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)
  
  template = loader.get_template('product/vends/shop.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'current': current,
    'p_sum': p_sum,
    'lid': search,
    'cat': 0,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))

@login_required


def slists(request,uidb64):
  search=force_str(urlsafe_base64_decode(uidb64))
  cats =  Categories.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True).exclude(id=search)
  current =  Shops.objects.get(id=search)
  
  prods =  Vproducts.objects.filter(Q(shop__id__iexact=search),status=True)
  p_sum=prods.count()
  
  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 8)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)
  
  template = loader.get_template('product/vends/shop_list.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'current': current,
    'p_sum': p_sum,
    'lid': search,
    'cat': 0,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))

@login_required


def listing(request,sidb64,uidb64):
  search=force_str(urlsafe_base64_decode(uidb64))
  shop=force_str(urlsafe_base64_decode(sidb64))
  cats =  Categories.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True).exclude(id=shop)
  current =  Shops.objects.get(id=shop)
  
  prods =  Vproducts.objects.filter(Q(shop__id__iexact=shop),Q(product__category__id__iexact=search),status=True)
  p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)
  
  
  template = loader.get_template('product/vends/shop.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'current': current,
    'p_sum': p_sum,
    'cat': 1,
    'lid': search,
    'sid': shop,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))



@login_required


def slisting(request,sidb64,uidb64):
  search=force_str(urlsafe_base64_decode(uidb64))
  shop=force_str(urlsafe_base64_decode(sidb64))
  cats =  Categories.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  discounts =  Vproducts.objects.filter(status=True)
  shops =  Shops.objects.filter(status=True).exclude(id=shop)
  current =  Shops.objects.get(id=shop)
  
  prods =  Vproducts.objects.filter(Q(shop__id__iexact=shop),Q(product__category__id__iexact=search),status=True)
  p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)
  
  
  template = loader.get_template('product/vends/shop_list.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'shops': shops,
    'current': current,
    'p_sum': p_sum,
    'cat': 1,
    'lid': search,
    'sid': shop,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))


@login_required


def allvendors(request):
  docs = LegalDocuments.objects.filter(type__is_global=True)
  prods =  Shops.objects.filter(status=True)
  p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)
  
  
  template = loader.get_template('product/vends/vendors.html')
  context = {
    
    'products': products,
    'p_sum': p_sum,
    'docs': docs,
    
  }
  return HttpResponse(template.render(context, request))





