from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products
from vendors.models import Shops
from management.models import Counties
from accounts.models import CustomUser,CompanyMeta
from core.models import OrderCarts,Orders, Responses, Reviews, Tracker
from django.contrib import messages
from django.db.models import Sum, Count
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta, time, date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, experts_watch
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
@experts_watch
def index(request):
  products = OrderCarts.objects.filter(vproduct__shop__vendor=request.user.id, status=0).values('vproduct__shop','serial','status').annotate(dcount=Count('serial')).order_by()
  template = loader.get_template('eorders/pending.html')
  context = {
    'products': products,
    'ptitle': 'Pending',
  }
  return HttpResponse(template.render(context, request))

@login_required
@experts_watch
def delay(request):
  meta= CompanyMeta.objects.get(id=1)

  time_threshold = datetime.now() - timedelta(hours=meta.dd_vendor)
  products = OrderCarts.objects.filter(vproduct__shop__vendor=request.user.id,created_at__lt=time_threshold, status=0).values('vproduct__shop','serial','status').annotate(dcount=Count('serial')).order_by()
  template = loader.get_template('eorders/pending.html')
  context = {
    'products': products,
    'ptitle': 'Delayed_Dispatch',
  }
  return HttpResponse(template.render(context, request))




@login_required
@experts_watch
def closed(request):
  meta= CompanyMeta.objects.get(id=1)
  products = OrderCarts.objects.filter(vproduct__shop__vendor=request.user.id).exclude(status__lt=1).values('vproduct__shop','serial','status').annotate(dcount=Count('serial')).order_by()
  template = loader.get_template('eorders/pending.html')
  context = {
    'products': products,
    'ptitle': 'Processed',
  }
  return HttpResponse(template.render(context, request))


@login_required
@experts_watch
def tracker(request):
  meta= CompanyMeta.objects.get(id=1)

  products = Tracker.objects.filter(vendor=request.user.id,status=False)
  template = loader.get_template('eorders/track.html')
  context = {
    'products': products,
    'ptitle': 'On_Transit',
  }
  return HttpResponse(template.render(context, request))

@login_required
@experts_watch
def ctracker(request):
  meta= CompanyMeta.objects.get(id=1)

  products = Tracker.objects.filter(vendor=request.user.id,status=True)
  template = loader.get_template('eorders/track.html')
  context = {
    'products': products,
    'ptitle': 'Completed',
  }
  return HttpResponse(template.render(context, request))


@login_required
@experts_watch
def dtracker(request):
  meta= CompanyMeta.objects.get(id=1)
  time_threshold = datetime.now()
  

  products = Tracker.objects.filter(vendor=request.user.id,eta__lt=time_threshold,status=False)
  template = loader.get_template('eorders/track.html')
  context = {
    'products': products,
    'ptitle': 'Delivery_Tracking(Delays)',
  }
  return HttpResponse(template.render(context, request))

@login_required
@experts_watch
def edita(request, id):
  part1 = id.split(".",1)[0]
  part2 = id.split(".",1)[1]
  serial = str(part1)
  shop = int(part2)

  
  
  
  parameters = { 'serial': serial, 'shop': shop, }
  
  
  response = parameters

  return JsonResponse(response, safe=False)

@login_required
@experts_watch
def updaterecord(request):
  action = request.POST['dispatch']
  c = request.POST['narration']
  id = request.POST['hidden_id']
  shp = request.POST['shop']
  myDate = datetime.now()
  
  

  OrderCarts.objects.filter(vproduct__shop__vendor=request.user.id, serial=id).update(status=action,note=c,action_at=myDate)
  

  code = get_random_string(length=10)
  u_id = 'TRXCN:'+code

  vendor = CustomUser.objects.get(id=request.user.id)
  shop = Shops.objects.get(id=shp)
  
  tracker = Tracker(tid=u_id, sid=id, vendor=vendor,shop=shop, eta= request.POST['eta'], note=c,transport=request.POST['transport'],action_at = myDate)
  tracker.save()
  
  if action == '1':
  
   response = {
        'success':'Order Dispatched successfully.' 
            }

  else:
       response = {
        'success':'Cancellation Request Submitted successfully.' 
            }

  return JsonResponse(response)

@login_required
@experts_watch
def order_detail(request,serial):
  
  items = OrderCarts.objects.filter(vproduct__shop__vendor=request.user.id,serial=serial)
  stat = OrderCarts.objects.filter(vproduct__shop__vendor=request.user.id,serial=serial).first()
  order = Orders.objects.get(serial=serial)
  meta = CompanyMeta.objects.get(id=1)
  cust = CustomUser.objects.get(id=order.customer.id)
  template = loader.get_template('eorders/order.html')
  context = {
    'items': items,
    'order': order,
    'meta': meta,
    'cust': cust,
    'stat': stat,
    
  }
  return HttpResponse(template.render(context, request))

@login_required
@experts_watch
def sales_filter(request):
  countys = Shops.objects.filter(vendor=request.user.id)
  template = loader.get_template('eorders/filter.html')
  context = {
    'products': 1,
    'countys' : countys
    
  }
  return HttpResponse(template.render(context, request))

@login_required
@experts_watch
def sales_report(request):
  if request.method =='GET':
    
    start = request.GET['start']
    end = request.GET['end']
    shop = int(request.GET['shop'])
    ds= datetime.strptime(start, '%Y-%m-%d')
    de= datetime.strptime(end, '%Y-%m-%d')
    star =  ds.strftime("%d/%m/%Y")
    en =  de.strftime("%d/%m/%Y")
    

    url = 'csrfmiddlewaretoken='+request.GET['csrfmiddlewaretoken']+'&shop='+request.GET['shop']+\
    '&start='+request.GET['start']+'&end='+request.GET['end']+'&action_button='+request.GET['action_button']
   
    if shop == 0:
     duka='All Shops'
  
     prods = OrderCarts.objects.filter(vproduct__shop__vendor=request.user.id,created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).values('id','serial','created_at','status').annotate(dcount=Count('serial')).order_by('-id')
 
     total= OrderCarts.objects.filter(vproduct__shop__vendor=request.user.id,created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).aggregate(sum=Sum('final_price'))
    else:
         loc= Shops.objects.get(id=shop)
         duka = loc.name
         prods = OrderCarts.objects.filter(vproduct__shop=shop,vproduct__shop__vendor=request.user.id,created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).values('id','serial','created_at','status').annotate(dcount=Count('serial')).order_by('-id')
 
         total= OrderCarts.objects.filter(vproduct__shop=shop,vproduct__shop__vendor=request.user.id,created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).aggregate(sum=Sum('final_price'))

    if  total['sum'] == None:
        count=0
     
    else:
        count= total['sum']

    page = request.GET.get('page', 1)

    paginator = Paginator(prods, 10)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

        
    ptitle='Sales'
 
    template = loader.get_template('eorders/sales.html')
    context = {
    'products': products,
    'ptitle': ptitle,
    'star': star,
    'en' : en,
    'count' : count,
    'duka' : duka,
    'url' : url,
   
    
        }
   
    return HttpResponse(template.render(context, request))
  else:
    messages.success(request,'Invalid Request !')
    return redirect('/vendors/sales_filter/')



@login_required
@experts_watch
def nreviews(request):
  title='New'
  countys = Reviews.objects.filter(vproduct__shop__vendor=request.user.id,is_viewed=False)
  template = loader.get_template('ereview/review.html')
  context = {
    'ptitle': title,
    'actives' : countys
    
  }
  return HttpResponse(template.render(context, request))

@login_required
@experts_watch
def allreviews(request):
  title='All'
  countys = Reviews.objects.filter(vproduct__shop__vendor=request.user.id)
  template = loader.get_template('ereview/review.html')
  context = {
    'ptitle': title,
    'actives' : countys
    
  }
  return HttpResponse(template.render(context, request))


@login_required
@experts_watch
def checkreview(request, id):
  xv= Reviews.objects.get(id=id)
  mymember = model_to_dict(Reviews.objects.get(id=id))

  if not xv.is_viewed:
    check= Reviews.objects.get(id=id)
    check.is_viewed = True
    check.save()
  
  response = mymember

  return JsonResponse(response, safe=False)


@login_required
@experts_watch
def dconf(request, id):
  member = Tracker.objects.get(id=id)
  member.status=True
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)
