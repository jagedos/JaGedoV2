from django import template
from django.db.models import Sum, Count
from vendors.models import Vproducts, Shops
from items.models import Pimages, Products,Categories
from core.models import Carts, OrderCarts, Orders, Responses,Reviews, Tracker
from accounts.models import CompanyMeta,CustomUser
from datetime import datetime, timedelta, time, date
from django.utils.safestring import mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter
def today_sales(id):
    
    total= OrderCarts.objects.filter(shop__vendor=id,created_at__date=date.today()).exclude(status=3).aggregate(sum=Sum('final_price'))
    if  total['sum'] == None:
        count=0
     
    else:
        count= total['sum']
    
    final = count
    return final 

@register.filter
def todays_revs(id):
    num =Reviews.objects.filter(shop__vendor=id,is_viewed=False,created_at__date=date.today()).count()
    final = num
    return final 

@register.filter
def shop_products(id):
    total= Vproducts.objects.filter(shop=id,status=True).count()
    final = total
    return final 

@register.filter
def pending(id):
    total= OrderCarts.objects.filter(shop__vendor=id,status=0).values('serial').annotate(dcount=Count('serial')).count()
    final = total
    return final 

@register.filter
def singletotal(id):
   total= OrderCarts.objects.filter(serial=id).aggregate(sum=Sum('final_price'))
   if  total['sum'] == None:
        count=0
     
   else:
        count= total['sum']
    
   final = count
   return final 
   
   
@register.filter
def delays(id):
    meta= CompanyMeta.objects.get(id=1)

    time_threshold = datetime.now() - timedelta(hours=meta.dd_vendor)
    total= OrderCarts.objects.filter(shop__vendor=id,created_at__lt=time_threshold,status=0).values('serial').annotate(dcount=Count('serial')).count()
    final = total
    return final 

@register.filter
def delaysdel(id):
    meta= CompanyMeta.objects.get(id=1)

    time_threshold = datetime.now() 
    total= Tracker.objects.filter(eta__lt=time_threshold,status=False).count()
    final = total
    return final 


@register.filter
def delpending(id):
    meta= CompanyMeta.objects.get(id=1)

    
    total= Tracker.objects.filter(status=False).count()
    final = total
    return final 




@register.filter
def items(id):
   prs= OrderCarts.objects.filter(serial=id)
   if prs.exists():
     button=''
     for p in prs:
       if  p.pk % 2 == 0:
          button+='<p class="btn bg-green btn-xs btn-sm">'+str(p.vproduct.name)+'</p>'+' x '+\
          '<p class="btn bg-navy btn-xs btn-sm">'+str(p.quantity)+' '+str(p.vproduct.units)+'</p>'+' , '+'<p>'+'</p>'
     
       else:
           button+='<p class="btn bg-pink btn-xs btn-sm">'+str(p.vproduct.name)+'</p>'+' x '+\
          '<p class="btn bg-navy btn-xs btn-sm">'+str(p.quantity)+' '+str(p.vproduct.units)+'</p>'+' , '+'<p>'+'</p>'
   else:
    button='N/A'

   final = button
   return final 

@register.filter
def unverified(id):
   
    total= Tracker.objects.filter(sid=id).count()
    final = total
    return final 


@register.simple_tag
def itemsfind(serial,shop):
  
   prs= OrderCarts.objects.filter(serial=serial,shop=shop)
   button=''
   for p in prs:
    if  p.id % 2 == 0:
        button+='<p class="btn bg-green btn-xs btn-sm">'+str(p.vproduct.name)+'</p>'+' x '+\
          '<p class="btn bg-navy btn-xs btn-sm">'+str(p.quantity)+' '+str(p.vproduct.units)+'</p>'+' , '+'<p>'+'</p>'
     
    else:
        button+='<p class="btn bg-pink btn-xs btn-sm">'+str(p.vproduct.name)+'</p>'+' x '+\
          '<p class="btn bg-navy btn-xs btn-sm">'+str(p.quantity)+' '+str(p.vproduct.units)+'</p>'+' , '+'<p>'+'</p>'
    
   final = mark_safe(button)
   return final 

@register.simple_tag
def vsingletotal(serial,shop):
   total= OrderCarts.objects.filter(serial=serial,shop=shop).aggregate(sum=Sum('final_price'))
   if  total['sum'] == None:
        count=0
     
   else:
        count= intcomma(total['sum'])
    
   final = count
   return final 



@register.simple_tag
def vconcat(serial,shop):
   final = str(serial)+"."+str(shop)
   return final 


@register.simple_tag
def fvendors(serial,shop):
   meta=OrderCarts.objects.filter(shop=shop, serial=serial).first()
   det= str(meta.shop.vendor)+" "+"<br>"+str(meta.shop.name)
   final = mark_safe(det)
   return final 

@register.filter
def itemsc(id):
   prs= OrderCarts.objects.filter(id=id)
   button=''
   for p in prs:
    if  p.id % 2 == 0:
        button+='<p class="badge bg-success ">'+str(p.vproduct.product.name)+'</p>'+' x '+\
          '<p class="badge bg-secondary">'+str(p.quantity)+' '+str(p.vproduct.product.units)+'</p>'+' , '+'<p>'+'</p>'
     
    else:
        button+='<p class="badge bg-primary ">'+str(p.vproduct.product.name)+'</p>'+' x '+\
          '<p class="badge bg-secondary ">'+str(p.quantity)+' '+str(p.vproduct.product.units)+'</p>'+' , '+'<p>'+'</p>'
    
   final = button
   return final 

@register.filter
def itemsm(id):
   prs= Carts.objects.filter(id=id)
   button=''
   for p in prs:
    if  p.id % 2 == 0:
        button+='<p class="btn bg-green btn-xs btn-sm">'+str(p.vproduct.product.name)+'</p>'+' x '+\
          '<p class="btn bg-navy btn-xs btn-sm">'+str(p.quantity)+' '+str(p.vproduct.product.units)+'</p>'+' , '+'<p>'+'</p>'
     
    else:
        button+='<p class="btn bg-green btn-xs btn-sm">'+str(p.vproduct.product.name)+'</p>'+' x '+\
          '<p class="btn bg-navy btn-xs btn-sm">'+str(p.quantity)+' '+str(p.vproduct.product.units)+'</p>'+' , '+'<p>'+'</p>'
    
   final = button
   return final 



@register.filter
def customer(id):
    tot= Orders.objects.filter(serial=id)
    if tot.exists():
        total= Orders.objects.get(serial=id)
        final = mark_safe(total.customer.first_name+' '+total.customer.last_name+'<br />'+total.customer.phone_number)
    else:
        final = 'N/A'

    
    return final 



@register.filter
def orderid(id):
    total= Orders.objects.get(serial=id)
    final = total.id
    return final 


@register.filter
def not_dispatched(id):
     checks= OrderCarts.objects.filter(serial=id,status=0)
     if checks.exists():
         final=1
     else:
         final=0

     return final

@register.filter
def vendor_find(id):
    total= Vproducts.objects.filter(shop=id).first()
    final = total.shop.vendor.first_name+' '+total.shop.vendor.last_name+'<br>'+total.shop.vendor.phone_number
    return final 


@register.filter
def svendor_find(id):
    total= Vproducts.objects.get(id=id)
    final = '<b>Shop :</b>'+' '+total.shop.name+'<br>'+'<b>Vendor :</b>'+total.shop.vendor.first_name+' '+total.shop.vendor.last_name+'<br>'+total.shop.vendor.phone_number
    return final 


@register.filter
def orderdate(id):
    total= Orders.objects.get(serial=id)
    final = total.created_at
    return final 


@register.simple_tag
def tstatus(serial,shop, user):
   tcheck = Tracker.objects.filter(sid=serial,shop=shop,vendor=user)
   if tcheck.exists():
       det=tcheck.first()
       if det.status:
           tx='<span class="btn btn-xs btn-success">Delivered</span>'
       else:
            tx= '<span class="btn btn-xs bg-gray">Pending</span>'

   else:
       tx=' <span class="btn btn-xs bg-gray">Pending</span>'
       
   final = mark_safe(tx)
   return final 