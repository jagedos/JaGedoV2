from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products
from vendors.models import Shops, Vproducts
from core.models import OrderCarts, Orders, Carts, Tracker
from management.models import Counties, CartMeta,PickUps
from accounts.models import CustomUser, CompanyMeta
from django.utils.crypto import get_random_string
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Count
from datetime import datetime, timedelta, time, date
import json
from django.db.models import Q
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required


def index(request):
  products = OrderCarts.objects.filter(status=0).values('serial','status').annotate(dcount=Count('serial')).order_by()
  template = loader.get_template('delivery/orders.html')
  context = {
    'products': products,
    'ptitle': 'Pending_Dispatch',
  }
  return HttpResponse(template.render(context, request))

def mdispatch(request,id):
  products = OrderCarts.objects.filter(serial=id,status=0).values('serial','shop','status').annotate(dcount=Count('shop')).order_by()
  template = loader.get_template('delivery/dispatch.html')
  context = {
    'products': products,
    'ptitle': 'Vendor_Dispatch',
  }
  return HttpResponse(template.render(context, request))


def delivery(request):
  products = Orders.objects.filter(status=1)
  template = loader.get_template('delivery/orders.html')
  context = {
    'products': products,
    'ptitle': 'Pending_Delivery',
  }
  return HttpResponse(template.render(context, request))

def delayed_dispatch(request):
  meta= CompanyMeta.objects.get(id=1)

  time_threshold = datetime.now() - timedelta(hours=meta.dd_office)
  products = Orders.objects.filter(created_at__lt=time_threshold,status=0)
  template = loader.get_template('delivery/orders.html')
  context = {
    'products': products,
    'ptitle': 'Pending_Dispatches',
  }
  return HttpResponse(template.render(context, request))


def delayed_delivery(request):
  time_threshold = datetime.now()
  products = Orders.objects.filter(eta__lt=time_threshold,status=1)
  template = loader.get_template('delivery/orders.html')
  context = {
    'products': products,
    'ptitle': 'Pending_Deliveries',
  }
  return HttpResponse(template.render(context, request))

def edita(request, id):
  part1 = id.split(".",1)[0]
  part2 = id.split(".",1)[1]
  serial = str(part1)
  shop = int(part2)

  
  
  
  parameters = { 'serial': serial, 'shop': shop, }
  response = parameters
  return JsonResponse(response, safe=False)



@login_required
@manager_watch
def updaterecord(request):
  action = request.POST['dispatch']
  c = request.POST['narration']
  id = request.POST['hidden_id']
  shop = request.POST['shop']
  myDate = datetime.now()
  
  meta=OrderCarts.objects.filter(shop=shop, serial=id).first()

  OrderCarts.objects.filter(shop=shop, serial=id).update(status=action,note=c,action_at=myDate)
  

  code = get_random_string(length=10)
  u_id = 'TRXCN:'+code

  vendor = CustomUser.objects.get(id=meta.vproduct.shop.vendor.pk)
  shop = Shops.objects.get(id=meta.vproduct.shop.pk)
  
  tracker = Tracker(tid=u_id, sid=id, vendor=vendor, shop=shop, eta= request.POST['eta'], note=c,transport=request.POST['transport'],action_at = myDate)
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



def delivered(request,id):
  action = 2
  
  myDate = datetime.now()
    
  member = Orders.objects.get(serial=id)
  member.status = 2
  member.del_at = myDate
  member.save()
  

  member = OrderCarts.objects.exclude(status=3).get(serial=id)
  member.status = action
  member.save()
  
  
  
  response = {
        'success':'Order Delivered successfully.' 
            }

  

  return JsonResponse(response)



def delay(request):
  meta= CompanyMeta.objects.get(id=1)

  time_threshold = datetime.now() - timedelta(hours=meta.dd_vendor)
  products = OrderCarts.objects.filter(created_at__lt=time_threshold, status=0).values('shop','serial','status').annotate(dcount=Count('shop')).order_by()
  template = loader.get_template('delivery/vorders.html')
  context = {
    'products': products,
    'ptitle': 'Delayed_Dispatch',
  }
  return HttpResponse(template.render(context, request))

def uprecord(request):
  action = request.POST['dispatch']
  c = request.POST['narration']
  id = request.POST['hidden_id']
  myDate = datetime.now()
  
  

  member = OrderCarts.objects.get(serial=id)
  member.status = action
  member.note = c
  member.action_at = myDate
  member.save()
  
  if action == '1':
  
   response = {
        'success':'Order Dispatched successfully.' 
            }

  else:
       response = {
        'success':'Cancellation Request Submitted successfully.' 
            }

  return JsonResponse(response)



def order_filter(request):
  products = CustomUser.objects.filter(is_customer=True,is_active=True)
  template = loader.get_template('delivery/pfilter.html')
  context = {
    'vendors': products,
    
  }
  return HttpResponse(template.render(context, request))



def vorders(request):
  if request.method =='GET':
    
    start = request.GET['start']
    end = request.GET['end']
    shop = int(request.GET['shop'])
    ds= datetime.strptime(start, '%Y-%m-%d')
    de= datetime.strptime(end, '%Y-%m-%d')
    star =  ds.strftime("%d/%m/%Y")
    en =  de.strftime("%d/%m/%Y")
  if shop == 0:
     duka='All Customers'
  
     prods = Orders.objects.filter(created_at__date__gte=start,created_at__date__lte=end)
   
   
  else:
         loc= CustomUser.objects.get(id=shop)
         duka = loc.first_name+' '+loc.last_name
         prods = Orders.objects.filter(customer=shop,created_at__date__gte=start,created_at__date__lte=end)
 
      
  
  template = loader.get_template('delivery/orders.html')
  context = {
    'products': prods,
    'ptitle': duka,
  }
  return HttpResponse(template.render(context, request))


def sales_Shop_filter(request):
  shops = Shops.objects.filter(status=True)
  template = loader.get_template('delivery/ssfilter.html')
  context = {
    'shops': shops,
    
  }
  return HttpResponse(template.render(context, request))



def sales_report(request):
  if request.method =='GET':
    
    start = request.GET['start']
    end = request.GET['end']
    shop = int(request.GET['shop'])
    ds= datetime.strptime(start, '%Y-%m-%d')
    de= datetime.strptime(end, '%Y-%m-%d')
    star =  ds.strftime("%d/%m/%Y")
    en =  de.strftime("%d/%m/%Y")
    
    url=1
   
    if shop == 0:
     duka='All Shops'
  
     products = OrderCarts.objects.filter(created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).values('id','serial','vproduct','created_at','status').annotate(dcount=Count('serial')).order_by('-id')
 
     total= OrderCarts.objects.filter(created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).aggregate(sum=Sum('final_price'))
    else:
         loc= Shops.objects.get(id=shop)
         duka = loc.name
         products = OrderCarts.objects.filter(shop=shop,created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).values('id','serial','vproduct','created_at','status').annotate(dcount=Count('serial')).order_by('-id')
 
         total= OrderCarts.objects.filter(shop=shop,created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).aggregate(sum=Sum('final_price'))

    if  total['sum'] == None:
        count=0
     
    else:
        count= total['sum']

        
    ptitle='Sales'
 
    template = loader.get_template('delivery/sales.html')
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
    return redirect('/mans/vssfilter/')


def sales_Vendor_filter(request):
  shops = CustomUser.objects.filter(is_vendor=True,is_active=True)
  template = loader.get_template('delivery/svfilter.html')
  context = {
    'shops': shops,
    
  }
  return HttpResponse(template.render(context, request))

def vsales_report(request):
  if request.method =='GET':
    
    start = request.GET['start']
    end = request.GET['end']
    shop = int(request.GET['shop'])
    ds= datetime.strptime(start, '%Y-%m-%d')
    de= datetime.strptime(end, '%Y-%m-%d')
    star =  ds.strftime("%d/%m/%Y")
    en =  de.strftime("%d/%m/%Y")
    
    url=2
   
    if shop == 0:
     duka='All Vendors'
  
     products = OrderCarts.objects.filter(created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).values('id','serial','vproduct','created_at','status').annotate(dcount=Count('serial')).order_by('-id')
 
     total= OrderCarts.objects.filter(created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).aggregate(sum=Sum('final_price'))
    else:
         loc= CustomUser.objects.get(id=shop)
         duka = loc.first_name+' '+loc.last_name+' | '+loc.phone_number
         products = OrderCarts.objects.filter(shop__vendor=shop,created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).values('id','serial','vproduct','created_at','status').annotate(dcount=Count('serial')).order_by('-id')
 
         total= OrderCarts.objects.filter(shop__vendor=shop,created_at__date__gte=start,created_at__date__lte=end).exclude(status=3).aggregate(sum=Sum('final_price'))

    if  total['sum'] == None:
        count=0
     
    else:
        count= total['sum']

        
    ptitle='Sales'
 
    template = loader.get_template('delivery/sales.html')
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
    return redirect('/mans/vsvfilter/')



def vendor_order_filter(request):
  shops = CustomUser.objects.filter(is_vendor=True,is_active=True)
  template = loader.get_template('delivery/vfilter.html')
  context = {
    'shops': shops,
    
  }
  return HttpResponse(template.render(context, request))


def vendororders(request):
  if request.method =='GET':
    
    start = request.GET['start']
    end = request.GET['end']
    shop = int(request.GET['shop'])
   
    if shop == 0:
        products = OrderCarts.objects.filter(created_at__date__gte=start,created_at__date__lte=end).values('serial','vproduct','shop','created_at','status').annotate(dcount=Count('serial')).order_by()

    else:
        products = OrderCarts.objects.filter(shop__vendor=shop,created_at__date__gte=start,created_at__date__lte=end).values('serial','vproduct','shop','created_at','status').annotate(dcount=Count('serial')).order_by()
 
    
    template = loader.get_template('delivery/vorders.html')
    context = {
    'products': products,
    'ptitle': 'Orders',
     }
    return HttpResponse(template.render(context, request))
  else:
    messages.success(request,'Invalid Request !')
    return redirect('/mans/vofilter/')

def customer_filter(request):
  
  template = loader.get_template('delivery/actfilter.html')
  context = {
    'shops': 1,
    
  }
  return HttpResponse(template.render(context, request))


# def vendororders(request):
#   if request.method =='GET':
    
#     shop = int(request.GET['customer'])
   
   
#     products = Carts.objects.filter(customer=shop)
    
#     cust = CustomUser.objects.get(id=shop)
#     cdet = '<b>Orders :</b>'+cust.first_name+' '+cust.last_name+' |'+cust.phone_number
    
#     template = loader.get_template('delivery/carts.html')
#     context = {
#     'products': products,
#     'ptitle': cdet,
#     'customer': shop,
#      }
#     return HttpResponse(template.render(context, request))
#   else:
#     messages.success(request,'Invalid Request !')
#     return redirect('/mans/act_filter/')



def delete(request, id):
  member = Carts.objects.get(id=id)
  member.delete()

  response = {
        'success':'Item Deleted successfully.' 
            }
  return JsonResponse(response)


def xdelete(request, id):
  member = Carts.objects.filter(customer=id)
  member.delete()

  response = {
        'success':'Item Deleted successfully.' 
            }
  return JsonResponse(response)




@login_required
@manager_watch
def tracker(request):
  meta= CompanyMeta.objects.get(id=1)

  products = Tracker.objects.filter(status=False)
  template = loader.get_template('delivery/track.html')
  context = {
    'products': products,
    'ptitle': 'In_Transit',
  }
  return HttpResponse(template.render(context, request))

@login_required
@manager_watch
def ctracker(request):
  meta= CompanyMeta.objects.get(id=1)

  products = Tracker.objects.filter(status=True)
  template = loader.get_template('delivery/track.html')
  context = {
    'products': products,
    'ptitle': 'Completed',
  }
  return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def dtracker(request):
  meta= CompanyMeta.objects.get(id=1)
  time_threshold = datetime.now()
  

  products = Tracker.objects.filter(eta__lt=time_threshold,status=False)
  template = loader.get_template('delivery/track.html')
  context = {
    'products': products,
    'ptitle': 'Delivery_Tracking(Delays)',
  }
  return HttpResponse(template.render(context, request))

@login_required
@manager_watch
def dconf(request, id):
  member = Tracker.objects.get(id=id)
  member.status=True
  member.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)


def torders(request):
  products = Orders.objects.filter(status=0).order_by()
  template = loader.get_template('delivery/torders.html')
  context = {
    'products': products,
    'ptitle': 'Unverified_Deliveries',
  }
  return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def vtracker(request,id):
  meta= CompanyMeta.objects.get(id=1)

  products = Tracker.objects.filter(sid=id,status=True)
  template = loader.get_template('delivery/vtrack.html')
  context = {
    'products': products,
    'ptitle': 'Delivery_Verification',
  }
  return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def vconf(request, id):
  member = Tracker.objects.get(id=id)
  member.is_confirmed=True
  member.save()

  sid=member.sid

  tcheck=Tracker.objects.filter(sid=sid,status=False)
  ocheck=OrderCarts.objects.filter(serial=sid, status=0)

  if tcheck.exists():
   x=0
  elif ocheck.exists():
   x=0
  else:
    membr = Orders.objects.get(serial=sid)
    membr.status=2
    membr.save()

  response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

def forders(request):
  products = Orders.objects.filter(status=2).order_by()
  template = loader.get_template('delivery/torders.html')
  context = {
    'products': products,
    'ptitle': 'Fullfilled_Orders',
  }
  return HttpResponse(template.render(context, request))


def unorders(request):
  shops = Shops.objects.filter(status=True)
  products = OrderCarts.objects.filter(is_assigned=0,status=0).values('serial','status').annotate(dcount=Count('serial')).order_by()
  template = loader.get_template('delivery/uorders.html')
  context = {
    'products': products,
    'ptitle': 'UnAssigned',
    'shops': shops,
  }
  return HttpResponse(template.render(context, request))


# assign shop to order

def assign(request):
  if request.method =='POST':
    shop = int(request.POST['shop'])
    serial = request.POST['hidden_id']
    OrderCarts.objects.filter(serial=serial).update(is_assigned=1,shop_id=shop)
    Orders.objects.filter(serial=serial).update(is_assigned=1,shop_id=shop)
    
    response = {
        'success':'Order Assigned successfully.' 
            }
    return JsonResponse(response)
  else:
    response = {
        'success':'Invalid Request !' 
            }
    return JsonResponse(response)
