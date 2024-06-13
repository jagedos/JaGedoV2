from unicodedata import category
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
import json, random, africastalking, re
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.contrib import messages
from django.core import serializers
from django.db.models import Sum
from items.models import Categories, Products, Pimages
from vendors.models import Vproducts,Shops
from core.models import Carts, OrderCarts, Orders, PCarts, Pcategories,jobs, TpayCarts
from accounts.models import CustomUser, CompanyMeta, Profile, Tkeys
from management.models import PickUps,Counties
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
import json
from django.utils.crypto import get_random_string
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
@customer_watch

def addrecord(request):
  if request.method =='POST':
     x = request.POST['vproduct']
     y = request.POST['quantity']
     z = request.user.id

     check = Carts.objects.filter(vproduct=x,customer=z)
     if check.exists():

        response = {
            'errors':'This Products Already Exists In Your Cart!' 
            }
        return JsonResponse(response)



     else:
        vproduct = Vproducts.objects.get(id=x)
        user = CustomUser.objects.get(id=z)
  
        member = Carts(vproduct=vproduct,quantity=y,customer=user)
        member.save()
        total=Carts.objects.filter(customer=user).aggregate(sum=Sum('quantity'))
        count= total['sum']

        response = {
          'success':'Product Added successfully To Cart.' ,
          'count' : count
            }
        return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)



@login_required
@customer_watch

def quickadd(request):
  if request.method =='GET':
     x = request.GET['vproduct_id']
     y = request.GET['quantity']
     z = request.user.id

     check = Carts.objects.filter(vproduct=x,customer=z)
     if check.exists():
        Carts.objects.filter(vproduct=x,customer=z).update(quantity=y)

        pcarts=PCarts.objects.filter(customer=z)
        
        if pcarts.exists():
          ptotal=PCarts.objects.filter(customer=z).count()
          pcount=ptotal 
        else:
          pcount=0


        total=Carts.objects.filter(customer=z).aggregate(sum=Sum('quantity'))
        count= total['sum'] + pcount

        response = {
            'success':'Product Quantity Updated Successfully !',
            'count' : count 
            }
        return JsonResponse(response)



     else:
        vproduct = Products.objects.get(id=x)
        user = CustomUser.objects.get(id=z)
  
        member = Carts(vproduct=vproduct,quantity=y,customer=user)
        member.save()

        pcarts=PCarts.objects.filter(customer=user)
        
        if pcarts.exists():
          ptotal=PCarts.objects.filter(customer=user).count()
          pcount=ptotal 
        else:
          pcount=0

        total=Carts.objects.filter(customer=user).aggregate(sum=Sum('quantity'))
        count= total['sum'] + pcount

        response = {
          'success':'Product Added successfully To Cart.' ,
          'count' : count
            }
        return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)




@login_required
@customer_watch
def updaterecord(request):
  x = request.POST['quantity']

  id = request.POST['hidden_id']
 
  member = Carts.objects.get(id=id)
  member.quantity = x
  member.save()

  response = {
        'success':'Quantity Updated successfully.' 
            }
  return JsonResponse(response)


def c_quantity(request):
  x = int(request.GET['new_quantity'])
  id = request.GET['cart_id']
  
  
  
  
  member = Carts.objects.get(id=id)
  member.quantity = x
  member.save()

  response = {
        'success':'Quntity Updated successfully.' 
            }
            
  return JsonResponse(response)
@login_required
@customer_watch
def delete(request, id):
  user=request.user.id
  member = Carts.objects.get(id=id)
  member.delete()

  cnum = Carts.objects.filter(customer=user).count()
  if cnum <= 0:
    TpayCarts.objects.filter(customer=user).delete()


  response = {
        'success':'Item Deleted successfully.' 
            }
  return JsonResponse(response)

def product_cart(request,uidb64):
  id = force_str(urlsafe_base64_decode(uidb64))
  items = Carts.objects.filter(customer=id)
  gigs = PCarts.objects.filter(customer=id)
  user = request.user.id
  prof = Profile.objects.filter(user=user).first()
  picks = PickUps.objects.all()
  cats = Pcategories.objects.all().order_by('-id')
  cat = Categories.objects.all().first()
  countys = Counties.objects.filter(status=True)
  template = loader.get_template('product/cart.html')
  context = {
    'items': items,
    'picks': picks,
    'countys': countys,
    'id': id,
    'gigs': gigs,
    'cats': cats,
    'cat': cat,
    'prof': prof,
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch
def gdelete(request, id):
  member = PCarts.objects.get(id=id)
  member.delete()

  response = {
        'success':'Request Deleted successfully.' 
            }
  return JsonResponse(response)

def encrypt_id(id):
    final = urlsafe_base64_encode(force_bytes(id))
    return final

@login_required
@customer_watch
def createorder(request):
  if request.method =='POST':
     client = request.POST['customer']
     delivery = int(request.POST['delivery_method'])
     final_price = request.POST['final_price']
     
     customer = CustomUser.objects.get(id=client)

     code = get_random_string(length=10)
     u_id = customer.phone_number+code
      
     if delivery == 1:
       picku = request.POST['pickup']
       loc = 48
       direct = 'None'
     else:
       picku = 2
       loc = request.POST['county_site']
       direct = request.POST['directions']

    
     county= Counties.objects.get(id=loc)
     pickup= PickUps.objects.get(id=picku)
     check = Carts.objects.filter(customer=client)
     pesacheck = TpayCarts.objects.filter(customer=client,is_paid=True)
     pcartsd = PCarts.objects.filter(Q(start__isnull=True),customer=client)
     pcarts = PCarts.objects.filter(customer=client)
     if pcartsd.exists():
        response = {
            'errors':'One Of Your Quotation Requests Has No Job Duration ! Kindly Provide it ' 
            }
        return JsonResponse(response)
     elif pcarts.exists() and not check.exists():
       if pcarts.exists():
           for p in pcarts:
             if p.is_direct:
               exp=p.product.expert.partner.pk
               expert = CustomUser.objects.get(id=exp)
             else:
               isdirect=False

             wrks=jobs()
             wrks.serial = u_id
             wrks.job = p.job
             wrks.rexpert = p.expert
             wrks.start = p.start
             wrks.end = p.end
             wrks.product = p.product
             wrks.quantity = p.quantity
             wrks.description = p.description
             wrks.delivery_method = delivery
             wrks.pickup= pickup
             wrks.location = county
             wrks.directions=direct
             wrks.customer = customer
             wrks.doc = p.doc
             if p.is_direct:
               wrks.is_direct = True
               wrks.has_expert = True
               wrks.expert = expert
             wrks.save()
           prev='None'
           PCarts.objects.filter(customer=client).update(doc=prev)

           PCarts.objects.filter(customer=client).delete()

           print(conmail(wrks.pk))

           messages.success(request, 'Quotation Request Successfully Made ! ')
           response = {
            'success':'Order Successfully Created!',
            'serial': u_id 
            }
           return JsonResponse(response)
       
     else:
       if check.exists() and  pesacheck.exists():
        
         for ch in check:
          vproduct = Products.objects.get(id=ch.vproduct.pk)
          discount = 0
          fin = vproduct.price - (vproduct.price*(0))
          final = round(float(fin), 2)

        
          member = OrderCarts(vproduct=vproduct,serial=u_id,quantity=ch.quantity,price=vproduct.price,discount=discount,final_price=final,customer=customer)
          member.save()
     
         memb = Orders(serial=u_id,final_price=final_price,has_paid=True,customer=customer,delivery_method=delivery,pickup=pickup,county=county,directions=direct)
         memb.save()

         Carts.objects.filter(customer=client).delete()
         TpayCarts.objects.filter(customer=client).delete()

         if pcarts.exists():
           for p in pcarts:
             if p.is_direct:
               exp=p.product.expert.partner.pk
               expert = CustomUser.objects.get(id=exp)
             else:
               isdirect=False

             wrks=jobs()
             wrks.serial = u_id
             wrks.job = p.job
             wrks.rexpert = p.expert
             wrks.start = p.start
             wrks.end = p.end
             wrks.product = p.product
             wrks.customer = customer
             wrks.quantity = p.quantity
             wrks.description = p.description
             wrks.delivery_method = delivery
             wrks.pickup= pickup
             wrks.location = county
             wrks.directions=direct
             wrks.doc = p.doc
             if p.is_direct:
               wrks.is_direct = True
               wrks.has_expert = True
               wrks.expert = expert
             wrks.save()

           prev='None'
           PCarts.objects.filter(customer=client).update(doc=prev)
           PCarts.objects.filter(customer=client).delete()


         print(conmail(memb.pk))

         messages.success(request, 'Order Successfully Created! ')
         response = {
            'success':'Order Successfully Created!',
            'serial': u_id 
            }
         return JsonResponse(response)

        
      
       else:
       
          response = {
            'errors':'This Cart Does Not Exist Or No Payment Received for This Order !' 
            }
          return JsonResponse(response)
      
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)

def conmail(id):
  meta = CompanyMeta.objects.get(id=1)

  checks = Orders.objects.filter(id=id)
  if checks.exists():
    chks = Orders.objects.get(id=id)
    user = CustomUser.objects.get(id=chks.customer.pk)
    first = user.first_name
    email = user.email
    serial = chks.serial
    
    subject = "Order Confirmation"
  
    htmltemp = loader.get_template('product/alerts/confirm_email.html')
    c = {
	  "email":email,
    "uname":first,
	  'domain': meta.url,
	  'site_name': meta.name,
	  'site_order': id,
    'serial': serial,
	  'protocol': meta.protocol,
					}
  else:
      chks = jobs.objects.get(id=id)
      user = CustomUser.objects.get(id=chks.customer.id)
      first = user.first_name
      email = user.email
      serial = encrypt_id(chks.serial)
    
      subject = "Quote_Request_Confirmation"
  
      htmltemp = loader.get_template('product/alerts/qconfirm_email.html')
      c = {
	      "email":email,
        "uname":first,
	      'domain': meta.url,
	      'site_name': meta.name,
	      'site_order': id,
        'serial': serial,
	      'protocol': meta.protocol,
					}

      
  html_content = htmltemp.render(c)
  try:
        msg = EmailMultiAlternatives(subject, html_content, 'JaGedo <alerts@jagedo.co.ke>', [user.email], headers = {'Reply-To': 'alerts@jagedo.co.ke'})
        msg.attach_alternative(html_content, "text/html")
        msg.send()
  except BadHeaderError:
        return HttpResponse('Invalid header found.')

  con_sms(id)
  msg='SUCCESS.'
  return msg



def con_sms(id):
  chk=Orders.objects.filter(id=id)
  if chk.exists():
    chks = chk.first()
  else:
    chks=jobs.objects.filter(id=id).first()

  user = CustomUser.objects.get(id=chks.customer.pk)
  num = user.phone_number
  phone = re.sub(r'^.', '+254', num).split(",")
  name = user.first_name
  if chk.exists():
     message =  "Dear "+name+",\n You order #0"+str(id)+" has been placed.\n You shall be alerted when the order is dispatched ."
  else:
    message =  "Dear "+name+",\n You quotation request #0"+str(id)+" has been placed.\n You shall be alerted when the quotation is ready ."

  items = Tkeys.objects.get()
  username =  items.u_name
  api_key =  items.u_key
  sender= "SUSRECOMM"

  africastalking.initialize(username, api_key)

  sms = africastalking.SMS

  sms.send(message, phone, sender)
    
 
   


  



@login_required
@customer_watch
def order_detail(request,serial):
  ord = Orders.objects.filter(serial=serial)
  if ord.exists():
    items = OrderCarts.objects.filter(serial=serial)
    order = ord.first()
    gigs = jobs.objects.filter(serial=serial)
    meta = CompanyMeta.objects.get(id=1)
    cust = CustomUser.objects.get(id=order.customer.pk)
    template = loader.get_template('product/order.html')
    context = {
      'items': items,
      'order': order,
      'meta': meta,
      'cust': cust,
      'gigs': gigs
    
      }
    return HttpResponse(template.render(context, request))
  else:
     items = jobs.objects.filter(serial=serial)
     order=items.first()
     meta = CompanyMeta.objects.get(id=1)
     cust = CustomUser.objects.get(id=order.customer.id)
     template = loader.get_template('product/jdetail.html')
     context = {
       'items': items,
       'meta': meta,
       'cust': cust,
       'order': order,
    
         }
     return HttpResponse(template.render(context, request))




@login_required
@customer_watch
def job_detail(request,uidb64):
  serial=force_str(urlsafe_base64_decode(uidb64))
  items = jobs.objects.filter(id=serial)
  order=items.first()
  meta = CompanyMeta.objects.get(id=1)
  cust = CustomUser.objects.get(id=order.customer.id)
  template = loader.get_template('product/jdetail.html')
  context = {
    'items': items,
    'meta': meta,
    'cust': cust,
    
  }
  return HttpResponse(template.render(context, request))