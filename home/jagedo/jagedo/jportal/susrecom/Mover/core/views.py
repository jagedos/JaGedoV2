from unicodedata import category
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products, Pimages
from vendors.models import Vproducts,Shops
from core.models import Carts, Reviews, Responses, OrderCarts, Orders, WishList, PCarts, TpayCarts
from mpesa.models import MpesaPayment
from accounts.models import Profile, CustomUser, CompanyMeta
from management.models import Counties, LegalDocuments, LegalDocumentTypes
from experts.models import Pitems, Pcategories, Peimages, PartnerMeta, PartnerCerts, PartnerSkills, PartnerTimes
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.db.models import Sum, Count, Max, Min, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required


# Create your views here.


def index(request):
  company =  CompanyMeta.objects.get(id=1)
  cat = Categories.objects.all().first()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  
  
  template = loader.get_template('jhome.html')
  context = {
    
    'meta': company,
    'cat': cat,
    'docs': docs,
    
  }
  return HttpResponse(template.render(context, request))

def hw(request):
  company =  CompanyMeta.objects.get(id=1)
  cats = Vproducts.objects.filter(status=True).values('product__category__id','product__category__name').annotate(dcount=Count('product__category__id'))
  discounts =  Vproducts.objects.filter(discount__gt=0,status=True).order_by('price')[:6]
  products =  Vproducts.objects.filter(status=True)[:6]
  slides =  Products.objects.filter(category__slide=True,slide=True,status=True)[:6]
  docs = LegalDocuments.objects.filter(type__is_global=True)
  template = loader.get_template('index.html')
  context = {
    'cats': cats,
    'products': products,
    'discounts': discounts,
    'company': company,
    'slides' : slides,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))



def about(request):
  company =  CompanyMeta.objects.get(id=1)
  cat = Categories.objects.all().first()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  
  template = loader.get_template('about.html')
  context = {
    
    'company': company,
    'cat': cat,
    'docs': docs,
    
  }
  return HttpResponse(template.render(context, request))

def cart_totals(request):
  if request.user.is_authenticated and request.user.is_customer:
  
    carts =  Carts.objects.filter(customer=request.user.id)
    pcarts=PCarts.objects.filter(customer=request.user.id)
    if pcarts.exists():
      ptotal=PCarts.objects.filter(customer=request.user.id).count()
      pcount= ptotal
    else:
      pcount=0

    if carts.exists():
      total=Carts.objects.filter(customer=request.user.id).aggregate(sum=Sum('quantity'))
      icount= total['sum']
    else:
      icount= 0
    
    count=pcount + icount
    
    response = {
        'count': count
            }
    return JsonResponse(response)
   
  else:
    response = {
        'count': 0 
            }
    return JsonResponse(response)

def cart_locations(request):
  locs =  Counties.objects.filter(status=True)
  activecounties='<ul class="main-category hover-category"><li class="location" id="48"><a href="#"> <i class="fal fa-solid fa-map-marker-alt category-icon"></i> KENYA </a></li>'
  for lc in locs:
    activecounties+='<li class="location" id="'+str(lc.id)+'"><a href="#"> <i class="fal fa-solid fa-map-marker-alt category-icon"></i> '+str(lc.name)+'</a></li>'
  activecounties+='</ul>'

   

  if request.user.is_authenticated and request.user.is_customer:
  
    carts =  Profile.objects.filter(user=request.user.id)
    if carts.exists():
      loc= Profile.objects.get(user=request.user.id)
      cty= loc.location.id
      if cty == 48:
        county='KENYA'
      else:
       county= loc.location.name
    
      response = {
        'county': county,
        'activecounties': activecounties
            }
      return JsonResponse(response)
    else:
      response = {
        'county': 'KENYA'
            }
      return JsonResponse(response)
  else:
    response = {
        'county': 'KENYA',
        'activecounties': activecounties 
            }
    return JsonResponse(response)


  
  
@login_required
def product_profile(request,uidb64):
  id = force_str(urlsafe_base64_decode(uidb64))
  items = Products.objects.get(id=id)
  imgs = Pimages.objects.filter(product=items.pk)
  cat = Categories.objects.all().first()
  products=  Products.objects.filter(status=True).exclude(id=id)[:12]
  r_prods=  Products.objects.filter(status=True,category=items.category).exclude(id=id)[:12]
  carts = Carts.objects.filter(vproduct=id)
  if carts.exists():
    cart = Carts.objects.get(vproduct=id)
  else:
    cart =""

  rviews =Reviews.objects.filter(vproduct=id,is_disabled=False)
  page = request.GET.get('page', 1)

  paginator = Paginator(rviews, 4)
  try:
        reviews = paginator.page(page)
  except PageNotAnInteger:
        reviews = paginator.page(1)
  except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

  template = loader.get_template('product/single.html')
  context = {
    'items': items,
    'products': products,
    'imgs': imgs,
    'r_prods': r_prods,
    'carts': carts,
    'cart': cart,
    'cat': cat,
    'id': id,
    'reviews': reviews,
  }
  return HttpResponse(template.render(context, request))

def find_review(request,id):
  checks = OrderCarts.objects.filter(vproduct=id,status=2,is_reviewed=False)
  if checks.exists():
    serials=checks.values_list('serial', flat=True)
    finder = Orders.objects.filter(serial__in=serials,customer=request.user.id)
    if finder.exists():
      locks=1
      udets=model_to_dict(finder.first())
    else:
      locks=0
      udets=""
  else:
    locks=0
    udets=""

  response = {
        'locks': locks,
        'udets': udets 
            }

  return JsonResponse(response)

@login_required
@customer_watch

def addreview(request):
  if request.method =='POST':
     y = request.POST['serial']
     rating = request.POST['rating']
     review = request.POST['review']
     p = request.POST['pid']
     z = request.user.id
     
     
     vproduct = Vproducts.objects.get(id=p)
     user = CustomUser.objects.get(id=z)
  
     member = Reviews(vproduct=vproduct,serial=y,rating=rating,review=review,customer=user)
     member.save()

     cart = OrderCarts.objects.get(vproduct=vproduct,serial=y)
     cart.is_reviewed = True
     cart.save()

     response = {
          'success':'Review Added Succesfully .' 
            }
     return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)


@login_required
@customer_watch

def editreview(request):
  if request.method =='POST':
     id = int(request.POST['hidden_id'])
     rating = request.POST['rating']
     review = request.POST['review']
     

     cart = Reviews.objects.get(id=id)
     cart.rating = rating
     cart.review = review
     cart.save()

     response = {
          'success':'Review Edited Succesfully .' 
            }
     return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)

@login_required
@customer_watch

def addwish(request,id):
  if request.method =='GET':
     user = request.user.id
     prod = Vproducts.objects.get(id=id)
     customer = CustomUser.objects.get(id=user)
     
     check= WishList.objects.filter(vproduct=prod,customer=customer)
     
     if check.exists():
       response = {
          'errors':'Item Already Added To WishList .' 
            }


     else:
       member = WishList(vproduct=prod,customer=customer)
       member.save()

       response = {
          'success':'Product Saved Succesfully .' 
            }
            
     return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)

def pload(request, id):
  check =TpayCarts.objects.filter(customer=id)
  if check.exists():
    det=check.first()

    if det.is_paid:
       Carts.objects.filter(customer=id).update(is_paid=True)

   
  else:
    carts = Carts.objects.filter(customer=id)
    finl=0
    for c in carts:
        req = Products.objects.get(id=c.vproduct.id)
        price = req.price - (req.price*(0))
        fin = price * c.quantity
        finl+=fin
    amount=finl

    customer=CustomUser.objects.get(id=id)

    obj= Carts.objects.filter(customer=id).order_by('-id')[0]

    code= customer.first_name+str(obj.pk)

  
    memb = TpayCarts(pcode=code,amount=amount,paid=0, customer=customer)
    memb.save()

  pays =TpayCarts.objects.filter(customer=id).first()
  mymember = model_to_dict(pays)

  response = mymember

  return JsonResponse(response, safe=False)
  
def custom_page_not_found_view(request, exception):
    return render(request, "404.html", {})


def custom_server_error_view(request):
    return render(request, "500.html", {})

    



  
