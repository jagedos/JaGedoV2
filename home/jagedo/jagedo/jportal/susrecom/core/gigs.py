from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from accounts.models import CustomUser, Profile, Tkeys, CompanyMeta
from experts.models import Pitems, Pcategories, Peimages, PartnerMeta, PartnerCerts, PartnerSkills, PartnerTimes, ExpertCats, ExpertSkills
from accounts.models import CustomUser
from django.db.models import Sum
from vendors.models import Counties
from core.models import Reviews, PCarts , Carts
from items.models import Categories
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch, experts_watch
from django.contrib.auth.decorators import login_required
from management.models import Counties, LegalDocuments, LegalDocumentTypes

# Create your views here.


@login_required
def allpitems(request):
  company =  CompanyMeta.objects.get(id=1)
  slides = ExpertCats.objects.all()
  cat = Categories.objects.all().first()
  docs = LegalDocuments.objects.filter(type__is_global=True)

  

  
  template = loader.get_template('gigs/land.html')
  context = {
    'slides': slides,
    'company': company,
    'cat': cat,
    'docs': docs,
    
  }
  return HttpResponse(template.render(context, request))


@login_required

def findskills(request,uidb64):
  id = force_str(urlsafe_base64_decode(uidb64))
  cats= ExpertCats.objects.all()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  cat = Categories.objects.all().first()
  details= ExpertCats.objects.get(id=id)
  slides = ExpertSkills.objects.filter(category=id)
  skills = ExpertSkills.objects.all()
  p_sum=slides.count()


  
  template = loader.get_template('gigs/skills.html')
  context = {
    "id": id,
    "cats": cats,
    "dets": details,
    'slides': slides,
    'p_sum': p_sum,
    'skills': skills,
    'cat': cat,
    'docs': docs,
    
    
  }
  return HttpResponse(template.render(context, request))


@login_required

def finderskills(request,uidb64):
  id = force_str(urlsafe_base64_decode(uidb64))
  slides = ExpertSkills.objects.filter(id=id)
  find=slides.first()
  docs = LegalDocuments.objects.filter(type__is_global=True)
  cats= ExpertCats.objects.all()
  cat = Categories.objects.all().first()
  details= ExpertCats.objects.get(id=find.category.pk)
  skills = ExpertSkills.objects.all()
  p_sum=slides.count()

  
  template = loader.get_template('gigs/skills.html')
  context = {
    "id": id,
    "cats": cats,
    "dets": details,
    'slides': slides,
    'p_sum': p_sum,
    'skills': skills,
    'cat': cat,
    'docs': docs,
    
  }
  return HttpResponse(template.render(context, request))

def skillsget(request, id):
  products = ExpertSkills.objects.get(id=id)

  parameters = { 'id': products.pk,
                 'name': products.name,
                 'category': products.category.pk,
                 'catname': products.category.name,
                 'cover': str(products.cover),
                 'status': products.status,
                 

   }
  response = parameters

  return JsonResponse(response, safe=False)

# @login_required

# def allpitems(request):
#   prof = Profile.objects.get(user=request.user.id)
#   cats =  Pcategories.objects.all().order_by('-id')
#   if prof.location.id == 48:
#     prods =  Pitems.objects.filter(status=True)
#     p_sum=prods.count()
#   else:
#     prods =  Pitems.objects.filter(expert__location__id=prof.location.id,status=True)
#     p_sum=prods.count()

#   page = request.GET.get('page', 1)

#   paginator = Paginator(prods, 12)
#   try:
#         products = paginator.page(page)
#   except PageNotAnInteger:
#         products = paginator.page(1)
#   except EmptyPage:
#         products = paginator.page(paginator.num_pages)

  
#   template = loader.get_template('gigs/grid_listings.html')
#   context = {
#     'cats': cats,
#     'products': products,
#     'p_sum': p_sum,
    
#   }
#   return HttpResponse(template.render(context, request))

@login_required
def allpitemslists(request):
  prof = Profile.objects.get(user=request.user.id)
  cats =  Pcategories.objects.all().order_by('-id')
  if prof.location.id == 48:
    prods =  Pitems.objects.filter(status=True)
    p_sum=prods.count()
  else:
    prods =  Pitems.objects.filter(expert__location__id=prof.location.id,status=True)
    p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  
  template = loader.get_template('gigs/lists_listings.html')
  context = {
    'cats': cats,
    'products': products,
    'p_sum': p_sum,
    
  }
  return HttpResponse(template.render(context, request))

@login_required
def product_profile(request,uidb64):
  id = force_str(urlsafe_base64_decode(uidb64))
  items = Pitems.objects.get(id=id)
  docs = LegalDocuments.objects.filter(type__is_global=True)
  imgs = Peimages.objects.filter(product=id)
  products=  Pitems.objects.filter(status=True,expert=items.expert).exclude(id=id)
  r_prods=  Pitems.objects.filter(status=True,category=items.category).exclude(id=id)
  carts = PCarts.objects.filter(product=id)
  if carts.exists():
    cart = PCarts.objects.get(product=id)
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

  template = loader.get_template('gigs/single.html')
  context = {
    'items': items,
    'products': products,
    'imgs': imgs,
    'r_prods': r_prods,
    'carts': carts,
    'cart': cart,
    'id': id,
    'reviews': reviews,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))


@login_required
@customer_watch

def addrecord(request):
  if request.method =='POST':
     r = request.POST['category']
     x = request.POST['product']
     y = request.POST['quantity']
     z = request.user.id
     job= Pcategories.objects.get(id=r)

     check = PCarts.objects.filter(product=x,customer=z)
     if check.exists():

        response = {
            'errors':'This Item Already Exists In Your Cart!' 
            }
        return JsonResponse(response)



     else:
        product = Pitems.objects.get(id=x)
        user = CustomUser.objects.get(id=z)
        carts=Carts.objects.filter(customer=user)
  
        member = PCarts(job=job,product=product,quantity=y,customer=user,is_direct=True)
        member.save()

        if carts.exists(): 
          ctotal=Carts.objects.filter(customer=user).aggregate(sum=Sum('quantity'))
          ctots= ctotal['sum']
        else:
          ctots= 0


        total=PCarts.objects.filter(customer=user).count()
        count= total + ctots

        response = {
          'success':'Request Added To Cart Successfully.' ,
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
 
  member = PCarts.objects.get(id=id)
  member.quantity = x
  member.save()

  response = {
        'success':'Request Quantity Updated successfully.' 
            }
  return JsonResponse(response)



@login_required
@customer_watch

def quickadd(request):
  if request.method =='GET':
     x = request.GET['product_id']
     y = request.GET['quantity']
     z = request.user.id

     check = PCarts.objects.filter(product=x,customer=z)
     if check.exists():
        PCarts.objects.filter(product=x,customer=z).update(quantity=y)

        ctotal=Carts.objects.filter(customer=z).aggregate(sum=Sum('quantity'))
        ctots= ctotal['sum']

        total=PCarts.objects.filter(customer=z).count()
        count= total + ctots

        response = {
            'success':'Request Quantity Updated Successfully !',
            'count' : count 
            }
        return JsonResponse(response)



     else:
        product = Pitems.objects.get(id=x)
        job = Pcategories.objects.get(id=product.category.id)
        user = CustomUser.objects.get(id=z)
        carts=Carts.objects.filter(customer=user)

        member = PCarts(job=job,product=product,quantity=y,customer=user,is_direct=True)
        member.save()
         
        if carts.exists(): 
          ctotal=Carts.objects.filter(customer=user).aggregate(sum=Sum('quantity'))
          ctots= ctotal['sum']
        else:
          ctots= 0


        total=PCarts.objects.filter(customer=user).count()
        count= total + ctots

        response = {
          'success':'Request Added To Cart Successfully.' ,
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

def addrequest(request):
  if request.method =='POST':
     r = request.POST['category']
     x = request.POST['expert']
     start = request.POST['start']
     end = request.POST['end']
     doc = request.FILES.get('doc')
     description =  request.POST['description']
     z = request.user.id
     job= ExpertCats.objects.get(id=r)
     expert= ExpertSkills.objects.get(id=x)

     
        
     user = CustomUser.objects.get(id=z)
  
     member = PCarts()
     member.job = job
     member.expert = expert
     member.quantity = 1
     member.description = description
     member.start = start
     member.end = end
     if doc is not None:
        member.doc = doc
     member.customer = user
     member.save()
     carts=Carts.objects.filter(customer=user) 
     if carts.exists():
       ctotal=Carts.objects.filter(customer=user).aggregate(sum=Sum('quantity'))
       ctots= ctotal['sum']
     else:
       ctots= 0

     total=PCarts.objects.filter(customer=user).count()
     count= total + ctots

     response = {
          'success':'Request Added To Cart Successfully.' ,
          'count' : count
            }
     return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)

def finder(request,uidb64):
  search=force_str(urlsafe_base64_decode(uidb64))
  prof = Profile.objects.get(user=request.user.id)
  cats =  Pcategories.objects.all().order_by('-id')
  if prof.location.id == 48:
    prods =  Pitems.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search),status=True)
    p_sum=prods.count()
  else:
    prods =  Pitems.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search),expert__location__id=prof.location.id,status=True)
    p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  
  template = loader.get_template('gigs/filter_grid.html')
  context = {
    'cats': cats,
    'products': products,
    'p_sum': p_sum,
    'lid': search,
    
  }
  return HttpResponse(template.render(context, request))



def finderl(request,uidb64):
  search=force_str(urlsafe_base64_decode(uidb64))
  prof = Profile.objects.get(user=request.user.id)
  docs = LegalDocuments.objects.filter(type__is_global=True)
  cats =  Pcategories.objects.all().order_by('-id')
  if prof.location.id == 48:
    prods =  Pitems.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search),status=True)
    p_sum=prods.count()
  else:
    prods =  Pitems.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search),expert__location__id=prof.location.id,status=True)
    p_sum=prods.count()

  page = request.GET.get('page', 1)

  paginator = Paginator(prods, 12)
  try:
        products = paginator.page(page)
  except PageNotAnInteger:
        products = paginator.page(1)
  except EmptyPage:
        products = paginator.page(paginator.num_pages)

  
  template = loader.get_template('gigs/filter_lists.html')
  context = {
    'cats': cats,
    'products': products,
    'p_sum': p_sum,
    'lid': search,
    'docs': docs,
    
  }
  return HttpResponse(template.render(context, request))


def encrypt_id(id):
    final = urlsafe_base64_encode(force_bytes(id))
    return final
@login_required
def search(request):
  search= request.GET['search']
  
  


  products =  ExpertSkills.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search),status=True)[:10]
  

  res=''
  
  

  for px in products:
    id=encrypt_id(px.pk)
    res+='<li class="list-group-item " ><a href="/gsearch_listings/'+ str(id)+'"  > '+str(px.name)+' | <b>Category: </b>'+str(px.category.name)+'</a></li>'

  parameters = { 'res': res }
  response = parameters
  return JsonResponse(response)

def edita(request, id):
  products = PCarts.objects.get(id=id)
  
 

  res = {

     'id': products.pk,
     'quantity': products.quantity,
     'category': products.job.pk,
     'expert': products.expert.pk,
     'start': products.start,
     'end': products.end,
     'description': products.description,
     'doc': str(products.doc),
  }
  
      
      

  parameters = { 'x': res,  }
  response = parameters

  return JsonResponse(response)




def updatecreq(request):
 
  desc = request.POST['description']
  start = request.POST['start']
  end = request.POST['end']
  quantity = request.POST['quantity']
  doc = request.FILES.get('doc')
  
  if not start or not end:
    response = {
        'errors':'Kindly Provide The Job Duration' 
            }
  else:

   
  
    id = request.POST['hidden_id']
    member = PCarts.objects.get(id=id)
    member.start = start
    member.end = end
    member.quantity = quantity
    member.description = desc
    if doc is not None:
     member.doc = doc
    member.save()

  

    response = {
        'success':'Data Updated successfully.' 
            }
  return JsonResponse(response)

