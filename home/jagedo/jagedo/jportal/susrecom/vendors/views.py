from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from core.models import OrderCarts,Orders
from items.models import Categories, Products
from django.forms.models import model_to_dict
from accounts.models import CustomUser, Vdocs, CompanyMeta
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json, os
from django.db.models.fields.files import ImageFieldFile
from django.db.models import Sum, Count
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required
from management.models import Counties, LegalDocuments, LegalDocumentTypes



# Create your views here.
def get_file_extension(file):
    return os.path.splitext(file.name)[1].lower()

def is_allowed_file(file_extension, allowed_extensions):
    return file_extension in allowed_extensions

@login_required
@vendor_watch
def index(request):
  ldocs = LegalDocuments.objects.filter(type__is_partner=True)
  products = OrderCarts.objects.filter(shop__vendor=request.user.id).values('shop','serial','status').annotate(dcount=Count('serial')).order_by('serial')[:6]
  vdcs= Vdocs.objects.filter(vendor=request.user.id)
  if vdcs.exists():
     vdocs=0
  else:
    vdocs=1

  template = loader.get_template('vdash.html')
  context = {
    'products': products,
    'vdocs': vdocs,
    'ldocs': ldocs
  }
  return HttpResponse(template.render(context, request))


@login_required
@vendor_watch
def profile(request):
  vdocs= Vdocs.objects.filter(vendor=request.user.id).first()
  template = loader.get_template('settings/profile.html')
  context = {
    'i': 1,
    'vdocs': vdocs
  }
  return HttpResponse(template.render(context, request))
  
@login_required
@vendor_watch
def updaterecord(request):
 if request.method =='POST':
    first = request.POST['first_name']
    last = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    nid = request.POST['national_id']
    id = request.user.id

    
    
    
    member = CustomUser.objects.get(id=id)
    member.first_name = first
    member.last_name = last
    member.email = email
    member.phone_number = phone
    member.national_id = nid
    member.save()

    
    

    response = {
        'success':'Details Updated successfully.' 
            }
      
 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)

@login_required
@vendor_watch
def uploadDocs(request):
    if request.method == 'POST':
        idfront = request.FILES['n_id_front']
        idback = request.FILES['n_id_back']
        bizreg = request.FILES['biz_reg']
        taxcomp = request.FILES['tax_comp']
        uid = request.POST['hidden_id']

        allowed_id_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        allowed_other_extensions = ['.pdf']

        if not (is_allowed_file(get_file_extension(idfront), allowed_id_extensions) and is_allowed_file(get_file_extension(idback), allowed_id_extensions) and is_allowed_file(get_file_extension(bizreg), allowed_other_extensions) and is_allowed_file(get_file_extension(taxcomp), allowed_other_extensions)):
            response = {
                'errors': 'Invalid file format. Please upload image or PDF for ID front and back, and PDF for the rest of the files.'
            }
            return JsonResponse(response)

        vendor = CustomUser.objects.get(id=uid)

        check = Vdocs.objects.filter(vendor=uid)

        if check.exists():

            response = {
                'errors': 'Documents Already Uploaded. Kindy Go To Your Profile To Update'
            }

        else:
            member = Vdocs(idfront=idfront, idback=idback, bizreg=bizreg, taxcomp=taxcomp, vendor=vendor)
            member.save()

            response = {
                'success': 'Documents Uploaded Successfully.'
            }

    else:
        response = {
            'errors': 'Invalid Request!'
        }

    return JsonResponse(response)

@login_required
@vendor_watch
def uviews(request, id):
  uid = request.user.id

  dets = Vdocs.objects.get(vendor=uid)
  mymember = model_to_dict(dets)

  if id == 0:
    path=dets.idfront
  elif id == 1:
    path=dets.idback
  elif id == 2:
    path=dets.bizreg
  elif id == 3:
    path=dets.taxcomp

  cdets= CompanyMeta.objects.get(id=1)

 
  media = '<embed  src="http://docs.google.com/viewer?url='+str(cdets.protocol)+'://'+str(cdets.url)+'/media/'+str(path)+'&embedded=true" style="margin:0 auto; width:800px; height:800px;" frameborder="0"></iframe>'
  
      
      

  parameters = { 'media': media }
  response = parameters

  return JsonResponse(response)


@login_required
@vendor_watch
def editDocs(request):
 if request.method =='POST':
    type = int(request.POST['itype'])

    if type == 0:
       ndata = request.FILES['n_id_front']
    elif type == 1:
      ndata = request.FILES['n_id_back']
    elif type == 2:
      ndata = request.FILES['biz_reg']
    elif type == 3:
      ndata = request.FILES['tax_comp']
      

     

    uid = request.user.id
     

    check=Vdocs.objects.get(vendor = uid)
    if type == 0:
     check.idfront= ndata 
    elif type == 1:
     check.idback = ndata 
    elif type == 2:
      check.bizreg = ndata 
    elif type == 3:
      check.taxcomp = ndata 
   
    check.save()
    
    

    response = {
        'success':'Documents Updated Successfully.' 
            }

      
 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)



# get legal document by id
def vdocsview(request, id):
    doctype = request.GET.get('doctype')
   

    
    if doctype == 'idfront':
        document = Vdocs.objects.get(id=id)
        doc = str(document.idfront)
        doc_name = 'Id_Front'
    elif doctype == 'idback':
        document = Vdocs.objects.get(id=id)
        doc = str(document.idback)
        doc_name = 'Id_Back'
    elif doctype == 'bizreg':
        document = Vdocs.objects.get(id=id)
        doc = str(document.bizreg)
        doc_name = 'Business_Registration'
    elif doctype == 'taxcomp':
        document = Vdocs.objects.get(id=id)
        doc = str(document.taxcomp)
        doc_name = 'Tax_Compliance'
       

    parameters = {
        'name': doc_name,
        'document': doc,
    }

    return JsonResponse(parameters, safe=False)

