from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products
from vendors.models import Shops, Vproducts
from core.models import OrderCarts, Orders, Carts, Reviews, Responses
from management.models import Counties, CartMeta,PickUps
from accounts.models import CustomUser, CompanyMeta
from django.utils.crypto import get_random_string
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.views import LoginView
import json
from django.db.models import Q
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required


# Create your views here.



@login_required
@manager_watch
def index(request):
  picks=PickUps.objects.filter(status=True)
  countys=Counties.objects.filter(status=True)
  checki= CartMeta.objects.filter(admin=request.user.id)
  if checki.exists():
      cl= CartMeta.objects.get(admin=request.user.id)
      id= cl.customer.id
      client = cl.customer
      items = Carts.objects.filter(customer=cl.customer.id)
  else:
      client='None'
      items='None'
      id=0

  template = loader.get_template('pos/order.html')
  context = {
    'client': client,
    'checki': checki,
    'items': items,
    'id': id,
    'picks': picks,
    'countys': countys
    
  }
  return HttpResponse(template.render(context, request))

def getcusts(request):
    
    search = request.GET.get('q', None)
    if search:
     dat = CustomUser.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(phone_number__icontains=search), is_customer=True, is_active=True).values('id','first_name','last_name','phone_number')
     data = list(dat)
     response=data
     return JsonResponse(response, safe=False)
    else:
        return JsonResponse(data={'success': False,
                                          'errors': 'No mathing items found'})

def cartmeta(request):
    if request.method =='GET':
      admin= request.user.id
      client= request.GET['customer']
      checks= Carts.objects.filter(is_initiated=True,customer=client)
      checka= Carts.objects.filter(is_initiated=True,admin=admin)
      checki= CartMeta.objects.filter(admin=admin)
      if checks.exists():
          response = {
        'errors':'Sale Already Initiated For The Same Customer By Another Admin !' 
            }
      elif checka.exists() or checki.exists():
          response = {
        'errors':'Kindly Complete/Cancel Current Initiated Sale, Before Changing Customer !' 
            }
      else:
          adm = CustomUser.objects.get(id=admin)
          clt = CustomUser.objects.get(id=client)
          member = CartMeta(admin=adm,customer=clt)
          member.save()

          response = {
        'success':'Customer Succesfully Updated !', 'client' : client
            }

        


    else:
        response = {
        'errors':'Invalid Request !' 
            }

    return JsonResponse(response)

def price_check(id):
    req = Vproducts.objects.get(id=id)
    item =req.product.id
    price = round(req.price - (req.price*(req.discount/100)),2)
    check = Vproducts.objects.filter(product__id=item,price__lt=price,status=True)
    if check.exists():
       final = 0
    else:
        final = 1
    return final


def search(request):
  search= request.GET['search']
 
  products =  Products.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search) | Q(brand__name__icontains=search), status=True)[:10]
  
  res='<ul class="col-md-12 col-xs-12 dropdown-menu"  style="display:block; position:relative; padding:0.0rem 0;">'
  
  for px in products:
    check=price_check(px.pk)
    if check == 1 :
    
     res+='<li ><a href="#" id="'+str(px.pk)+'" class="addprod dropdown-item" > '+str(px.name)+' | <b>Category: </b>'+str(px.category)+' | <b>Brand: </b>'+str(px.brand)+'</a></li>'

  res+='</ul>'

  parameters = { 'res': res }
  response = parameters
  return JsonResponse(response)


def additem(request):
  if request.method =='GET':
     x = request.GET['id']
     z = request.user.id
     meta= CartMeta.objects.get(admin=z)
     c=meta.customer.id

     check = Carts.objects.filter(vproduct=x,customer=c)
     if check.exists():

        response = {
            'errors':'This Product Already Exists In Your Cart!' 
            }
        return JsonResponse(response)



     else:
        vproduct = Products.objects.get(id=x)
        user = CustomUser.objects.get(id=z)
        client = CustomUser.objects.get(id=c)
  
        member = Carts(vproduct=vproduct,quantity=1,customer=client,is_initiated=True,admin=user)
        member.save()
        response = {
          'success':'Product Added successfully To Cart.' 
            }
        return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
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



def delete(request, id):
  member = Carts.objects.get(id=id)
  member.delete()

  response = {
        'success':'Item Deleted successfully.' 
            }
  return JsonResponse(response)


def delall(request, id):
  
  
  check = Carts.objects.filter(customer=id)
  if check.exists():
   check.delete()

  member = CartMeta.objects.get(customer=id)
  member.delete()

  response = {
        'success':'Order Cancelled successfully.' 
            }
  return JsonResponse(response)

def delallx(request, id):
  
  member = CartMeta.objects.get(customer=id)
  member.delete()

  response = {
        'success':'Order Cancelled successfully.' 
            }
  return JsonResponse(response)

def createorder(request):
  if request.method =='POST':
     client = request.POST['customer']
     delivery = int(request.POST['delivery_method'])
     final_price = request.POST['final_price']
     
     omata=CartMeta.objects.get(admin=request.user.id)
     admin=CustomUser.objects.get(id=request.user.id)
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
     qcheck = Carts.objects.filter(vproduct__stock__lte=0,customer=client)
     check = Carts.objects.filter(customer=client)
     
     if check.exists():
      if not qcheck.exists():
       for ch in check:
        vproduct = Vproducts.objects.get(id=ch.vproduct.id)
        discount = vproduct.discount
        quant= vproduct.stock-ch.quantity
        fin = vproduct.price - (vproduct.price*(discount/100))
        final = round(float(fin), 2)

        mem = Vproducts.objects.get(id=vproduct.pk)
        mem.stock = quant
        mem.save()
        
        member = OrderCarts(vproduct=vproduct,serial=u_id,quantity=ch.quantity,price=vproduct.price,discount=discount,final_price=final,customer=customer,is_initiated=True,admin=admin)
        member.save()
     
       memb = Orders(serial=u_id,final_price=final_price,has_paid=True,customer=customer,delivery_method=delivery,pickup=pickup,county=county,directions=direct,is_initiated=True,admin=admin)
       memb.save()

       Carts.objects.filter(customer=client).delete()
       CartMeta.objects.filter(admin=request.user.id).delete()

       print(conmail(memb.pk))

       response = {
            'success':'Order Successfully Created!',
            'serial': u_id 
            }
       return JsonResponse(response)

      else:
        response = {
            'errors':'One Of The Products Is Out Of Stock ! Kindly Remove It ' 
            }
        return JsonResponse(response)
      
     else:
       
        response = {
            'errors':'No Items Added To This Cart ! Kindly Add The Products Required' 
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
    user = CustomUser.objects.get(id=chks.customer.id)
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
    html_content = htmltemp.render(c)
    try:
      msg = EmailMultiAlternatives(subject, html_content, 'JengaCart <jenga@susrecomm.co.ke>', [user.email], headers = {'Reply-To': 'jenga@susrecomm.co.ke'})
      msg.attach_alternative(html_content, "text/html")
      msg.send()
    except BadHeaderError:
            return HttpResponse('Invalid header found.')
  
    msg='SUCCESS.'
    return msg
    
 
  else:

   msg='FAIL'
   return msg


def order_detail(request,serial):
  
  items = OrderCarts.objects.filter(serial=serial)
  order = Orders.objects.get(serial=serial)
  meta = CompanyMeta.objects.get(id=1)
  cust = CustomUser.objects.get(id=order.customer.id)
  template = loader.get_template('pos/orec.html')
  context = {
    'items': items,
    'order': order,
    'meta': meta,
    'cust': cust,
    
  }
  return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def allreviews(request):
  title='All'
  countys = Reviews.objects.all()
  template = loader.get_template('reviews/review.html')
  context = {
    'ptitle': title,
    'actives' : countys
    
  }
  return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def checkreview(request, id):
  mymember = model_to_dict(Reviews.objects.get(id=id))

  
  response = mymember

  return JsonResponse(response, safe=False)

@login_required
@manager_watch
def activate(request, id):
  xv = Reviews.objects.get(id=id)

  if xv.is_disabled:
     member = Reviews.objects.get(id=id)
     member.is_disabled = False
     member.save()

  else:
     member = Reviews.objects.get(id=id)
     member.is_disabled = True
     member.save()
 
 
  
  response = {
        'success':'Data Adjusted successfully.' 
            }
  return JsonResponse(response)




   