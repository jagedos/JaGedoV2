from urllib import response
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.urls import reverse
from django.template import loader
from django.core import serializers
from django.views.generic import View, UpdateView
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from items.models import Categories, Products
from accounts.models import CustomUser,Profile , Tkeys, CompanyMeta, Vdocs
import json, random, africastalking, re
from accounts.forms import VsignUpForm
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from accounts.tokens import account_activation_token
from django.contrib.auth.hashers import make_password
from datetime import datetime
from vendors.models import Counties
from experts.models import PartnerTimes, PartnerCerts, PartnerMeta, PartnerSkills, Fields, Skills, Wdays, Certs, ContractorCategory, ContractorMeta, ContractorPortfolio, NcaFields
from django.conf import settings
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required
from django.db import transaction
import os

# Create your views here.
@login_required
@manager_watch

def index(request):
  reg = int(request.GET.get('expert'))
  if reg == 0:
      users = CustomUser.objects.filter(is_expert=True)
  elif reg == 4:
      users = CustomUser.objects.filter(is_expert=True, partnermeta__isnull=True)
  else:
      users = CustomUser.objects.filter(is_expert=True, partnermeta__regas=reg)
  locs = Counties.objects.all()
  fields = Fields.objects.all()
  certs= Certs.objects.all()
  img=''
  for c in certs:
    img+='<option value="'+str(c.pk)+'">'+ str(c.name) +'</option>'

  days= Wdays.objects.filter(status=True)
  dys=''
  for d in days:
    dys+='<option value="'+str(d.pk)+'">'+ str(d.name) +'</option>'

  utype='Experts_Register'
  
  
  template = loader.get_template('experts/regs/eregs.html')
  context = {
    'users': users,
    'ptitle': utype,
    'locs' : locs,
    'fields': fields,
    'days' : dys,
    'certs' : img
  }
  return HttpResponse(template.render(context, request))

# pending approval experts filter
@login_required
@manager_watch
def pending_filter(request):
    exp = 0
    template = loader.get_template("experts/regs/ereg_filter.html")
    context = {"users": 1, "exp": exp}
    return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def expert_filter(request):
    exp = 0
    template = loader.get_template("experts/regs/aereg_filter.html")
    context = {
        "users": 1,
        "exp": exp,
    }
    return HttpResponse(template.render(context, request))
  
@login_required
@manager_watch
def fpending_filter(request):
    exp = 1
    template = loader.get_template("experts/regs/ereg_filter.html")
    context = {
        "users": 1,
        "exp": exp,
    }
    return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def fexpert_filter(request):
    exp = 1
    template = loader.get_template("experts/regs/aereg_filter.html")
    context = {
        "users": 1,
        "exp": exp,
    }
    return HttpResponse(template.render(context, request))

@login_required
@manager_watch

def pindex(request):
  reg = int(request.GET.get('expert'))
  if reg == 0:
      users = CustomUser.objects.filter(is_expert=True,is_approved=False)
  elif reg == 4:
      users = CustomUser.objects.filter(is_expert=True,is_approved=False, partnermeta__isnull=True)
  else:
      users = CustomUser.objects.filter(is_expert=True,is_approved=False, partnermeta__regas=reg)

      
  locs = Counties.objects.all()
  fields = Fields.objects.all()
  certs= Certs.objects.all()
  img=''
  for c in certs:
    img+='<option value="'+str(c.pk)+'">'+ str(c.name) +'</option>'

  days= Wdays.objects.filter(status=True)
  dys=''
  for d in days:
    dys+='<option value="'+str(d.pk)+'">'+ str(d.name) +'</option>'

  utype='Experts_Pending_Approval'
  
  
  template = loader.get_template('experts/regs/eregs.html')
  context = {
    'users': users,
    'ptitle': utype,
    'locs' : locs,
    'fields': fields,
    'days' : dys,
    'certs' : img
  }
  return HttpResponse(template.render(context, request))



@login_required
@manager_watch
def edita(request, id):
  products = CustomUser.objects.get(id=id)
  prod = PartnerMeta.objects.filter(partner=id)
  mymember = model_to_dict(products)
  if prod.exists():
     prods=prod.first()
     parameters = { 'dets': mymember, 
                 'gender': prods.gender,
                 'yrs': prods.yrs,
                 'location': prods.location.id,
                 'regas': prods.regas                
                                
                }
  else:
      parameters = { 'dets': mymember,
                     'gender': 0,
                     'yrs': 0,
                     'location': 0,
                     'regas': 0   
                     
      }
      
                    
  response = parameters

  return JsonResponse(response, safe=False)


@login_required
@manager_watch
def conedita(request, id):
  products = CustomUser.objects.get(id=id)
  prod = ContractorMeta.objects.filter(partner=id)
  mymember = model_to_dict(products)
  if prod.exists():
     prods=prod.first()
     parameters = { 'dets': mymember, 
                 'county': products.profile.county.id,
                 'company_name': prods.company_name,
                 'company_email': prods.company_email,
                 'company_phone': prods.company_phone,         
                                
                }
  else:
      parameters = { 'dets': mymember,
                     'county': 0,
                     'company_name': '',  
                     'company_email': '',
                     'company_phone': '' 
                     
      }
      
                    
  response = parameters

  return JsonResponse(response, safe=False)




def edocs(request,id):
  meta = PartnerMeta.objects.filter(partner=id)
  mdet = meta.first()
  if not mdet.regas == 3:
        users = CustomUser.objects.filter(is_expert=True)
        locs = Counties.objects.all()
        if not meta.exists():
            fields = Fields.objects.all()
        else:
            fields = Fields.objects.all().exclude(id=mdet.field.id)

        certs= Certs.objects.all()
        img=''
        for c in certs:
            img+='<option value="'+str(c.pk)+'">'+ str(c.name) +'</option>'

        days= Wdays.objects.filter(status=True)
        dys=''
        for d in days:
            dys+='<option value="'+str(d.pk)+'">'+ str(d.name) +'</option>'
            
        exp = CustomUser.objects.get(id=id)
        utype= exp.first_name +' '+exp.last_name+' Details'


        
        skills = PartnerSkills.objects.filter(partner=id)
        docs= PartnerCerts.objects.filter(partner=id)
        times= PartnerTimes.objects.filter(partner=id)
        
        
        template = loader.get_template('experts/regs/edocs.html')
        context = {
            'users': users,
            'ptitle': utype,
            'locs' : locs,
            'fields': fields,
            'days' : dys,
            'certs' : img,
            'expertid' : id,
            'skills' : skills,
            'docs' : docs,
            'times' : times,
            'mdet' : mdet,
            'metas': meta
        }
  else:
     contractor = ContractorMeta.objects.filter(partner=id).first()
     cats = ContractorCategory.objects.prefetch_related('contractorportfolio_set').filter(partner=id)
     nca = NcaFields.objects.all()
     fields= Fields.objects.all().exclude(id=5)


     template = loader.get_template('experts/regs/cedocs.html')
     context = {
    'metas': meta ,
    'mdet' : mdet,
    'contractor': contractor,
    'cats': cats,
    'nca': nca,
    'fields': fields,
    'fundiid': id,
     }
     
  return HttpResponse(template.render(context, request))







def is_allowed_file(file_extension, allowed_extensions):
    return file_extension in allowed_extensions
@login_required
@manager_watch
def editmeta(request):
    if request.method == 'POST':
        allowed_cv_extensions = ['.pdf']
        allowed_id_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp']

        icv = request.FILES.get('cv')
        cv = 1 if icv is None else request.FILES['cv']

        idfrontc = request.FILES.get('id_front')
        idfront = 1 if idfrontc is None else request.FILES['id_front']

        idbackc = request.FILES.get('id_back')
        idback = 1 if idbackc is None else request.FILES['id_back']

        check = PartnerMeta.objects.get(id=request.POST['hidden_id'])

        if not cv == 1:
            cv_extension = os.path.splitext(cv.name)[1].lower()
            if is_allowed_file(cv_extension, allowed_cv_extensions):
                check.cv = cv
            else:
                return JsonResponse({'errors': 'CV must be a PDF file'})

        if not idfront == 1:
            idfront_extension = os.path.splitext(idfront.name)[1].lower()
            if is_allowed_file(idfront_extension, allowed_id_extensions):
                check.idfront = idfront
            else:
                return JsonResponse({'errors': 'Id_Front must be an image or a PDF file'})

        if not idback == 1:
            idback_extension = os.path.splitext(idback.name)[1].lower()
            if is_allowed_file(idback_extension, allowed_id_extensions):
                check.idback = idback
            else:
                return JsonResponse({'errors': 'Id_Back must be an image or a PDF file'})

        check.save()

        response = {
            'success': 'Details Updated successfully.'
        }
    else:
        response = {
            'errors': 'Invalid Request!'
        }

    return JsonResponse(response)


@login_required
@manager_watch
def editameta(request):
    if request.method == 'POST':
        allowed_cv_extensions = ['.pdf']
       

        acv = request.FILES.get('approval_doc')
        appdoc = 1 if acv is None else request.FILES['approval_doc']

        print(request.POST['adhidden_id'])


        check = PartnerMeta.objects.get(id=request.POST['adhidden_id'])

        if not appdoc  == 1:
            appdoc_extension = os.path.splitext(appdoc.name)[1].lower()
            if is_allowed_file(appdoc_extension, allowed_cv_extensions):
                check.approval_doc = appdoc
            else:
                return JsonResponse({'errors': 'Approval Document must be a PDF file'})

        check.save()
        
        CustomUser.objects.filter(id=check.partner.pk).update(is_approved=True)

        response = {
            'success': 'Details Updated successfully.'
        }
    else:
        response = {
            'errors': 'Invalid Request!'
        }

    return JsonResponse(response)



@login_required
@manager_watch
def changeskill(request):
 if request.method =='POST':
    afield = int(request.POST['field'])
    skills = request.POST.getlist('skills')
    uid = int(request.POST['uid'])
    
    field =Fields.objects.get(id=afield)
    partner = CustomUser.objects.get(id=uid)

    PartnerMeta.objects.filter(partner=uid).update(field=field)
    PartnerSkills.objects.filter(partner=uid).delete()
    
    for s in range(len(skills)):
      pskill = skills[s]
      skil = Skills.objects.get(id=pskill)
      skill= PartnerSkills(field=field, skill=skil,partner=partner)
      skill.save()

    response = {
        'success':'Details Updated successfully.' 
            }

 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)


@login_required
@manager_watch
def addcerts(request):
    if request.method == 'POST':
        allowed_extensions = ['.pdf']
        
        cname = request.POST.getlist('cert_name')
        certs = request.FILES.getlist('certs')
        uid = int(request.POST['uid'])

        partner = CustomUser.objects.get(id=uid)

        for i in range(len(cname)):
            cert_name = cname[i]
            cert_file = certs[i]
            cert_extension = os.path.splitext(cert_file.name)[1].lower()

            if not is_allowed_file(cert_extension, allowed_extensions):
                return JsonResponse({'errors': 'Only PDF files are allowed for certificates'})

            certname = Certs.objects.get(id=cert_name)
            peps = PartnerCerts(cert=certname, doc=cert_file, partner=partner)
            peps.save()

        response = {
            'success': 'Details Updated successfully.'
        }
    else:
        response = {
            'errors': 'Invalid Request!'
        }

    return JsonResponse(response)


@login_required
@manager_watch
def addtimes(request):
 if request.method =='POST':
    availability = int(request.POST['aset'])
    day = request.POST.getlist('day')
    start = request.POST.getlist('start')
    end = request.POST.getlist('end')
    uid = int(request.POST['uid'])
    
    
    partner = CustomUser.objects.get(id=uid)

    PartnerMeta.objects.filter(partner=uid).update(availability=availability)
    
    if availability == 1:
          for a in range(len(day)):
            day_name = day[a]
            start_time = start[a]
            end_time = end[a]
            days= Wdays.objects.get(id=day_name)
            wrk = PartnerTimes(day=days, start=start_time, end=end_time, partner=partner)
            wrk.save()
    else:
      PartnerTimes.objects.filter(partner=uid).delete()


    response = {
        'success':'Details Updated successfully.' 
            }

 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)


# get legal document by id
def docsview(request, id):
    doctype = request.GET.get('doctype')
   

    if doctype == 'cv':
        document = PartnerMeta.objects.get(id=id)
        doc = str(document.cv)
        doc_name = 'CV'
    elif doctype == 'approval_doc':
        document = PartnerMeta.objects.get(id=id)
        doc = str(document.approval_doc)
        doc_name = 'Approval_Document'
    elif doctype == 'idfront':
        document = PartnerMeta.objects.get(id=id)
        doc = str(document.idfront)
        doc_name = 'Id_Front'
    elif doctype == 'idback':
        document = PartnerMeta.objects.get(id=id)
        doc = str(document.idback)
        doc_name = 'Id_Back'
    else:
        docs= PartnerCerts.objects.get(id=id)
        doc = str(docs.doc)
        doc_name = doctype

    parameters = {
        'name': doc_name,
        'document': doc,
    }

    return JsonResponse(parameters, safe=False)

# add contractor company details
@login_required
@transaction.atomic
def addcontractorcompany(request):
    # submit data to ContractorCategory and ContractorPortfolio
      if request.method =='POST':
        user = request.POST['chidden_id']
        company_name = request.POST['company_name']
        company_email = request.POST['company_email']
        company_phone = request.POST['company_phone']
        company_certificate = request.FILES['company_certificate']
        pin_cerfiticate = request.FILES['pin_certificate']
        business_permit = request.FILES['business_permit']
        company_profile = request.FILES['company_profile']
        allowed_certs = ['.pdf']

        # check if company_certificate is empty
        if company_certificate:
              company_certificate_extension = os.path.splitext(company_certificate.name)[1].lower()
              if not is_allowed_file(company_certificate_extension, allowed_certs):
                  return JsonResponse({'errors': 'Company Certificate must be a PDF file'})
        else:
            return JsonResponse({'errors': 'Company Certificate is required'})
        

        # check if pin_cerfiticate is empty
        if pin_cerfiticate:
              pin_cerfiticate_extension = os.path.splitext(pin_cerfiticate.name)[1].lower()
              if not is_allowed_file(pin_cerfiticate_extension, allowed_certs):
                  return JsonResponse({'errors': 'PIN Certificate must be a PDF file'})
        else:
            return JsonResponse({'errors': 'PIN Certificate is required'})
        
        # check if business_permit is empty
        if business_permit:
              business_permit_extension = os.path.splitext(business_permit.name)[1].lower()
              if not is_allowed_file(business_permit_extension, allowed_certs):
                  return JsonResponse({'errors': 'Business Permit must be a PDF file'})
        else:
            return JsonResponse({'errors': 'Business Permit is required'})
        
        # check if company_profile is empty
        if company_profile:
              company_profile_extension = os.path.splitext(company_profile.name)[1].lower()
              if not is_allowed_file(company_profile_extension, allowed_certs):
                  return JsonResponse({'errors': 'Company Profile must be a PDF file'})
        else:
            return JsonResponse({'errors': 'Company Profile is required'})
        
        # check if user has already submitted data in contractor meta
        if ContractorMeta.objects.filter(partner=user).exists():
          return JsonResponse({'errors': 'You have already submitted data for this company'})
        
        # check if user has already submitted data in contractor category
        if not ContractorCategory.objects.filter(partner=user).exists():
          return JsonResponse({'errors': 'You must submit atleast one company category '})
        

        # submit data to ContractorMeta
        meta = ContractorMeta(partner_id=user, company_name=company_name, company_email=company_email, company_phone=company_phone, company_cert=company_certificate, pin_cert=pin_cerfiticate, business_permit=business_permit, company_profile=company_profile)
        meta.save()

        Profile.objects.filter(user=user).update(has_details=True)
        response = {  'success':'Details Submitted successfully.' } 
  
      else:
        response = { 'errors':'Invalid Request!' }
  
      return JsonResponse(response)


@login_required
def addcontractormeta(request):
   # submit data to ContractorCategory and ContractorPortfolio
    if request.method =='POST':
       user = request.POST['hidden_id']
       field = request.POST['field']
       nca = request.POST['nca_class']
       # portfolio is a file
       portfolio = request.FILES['portfolio']
       allowed_portfolio_extensions = ['.pdf']

        # check if portfolio is empty
       if portfolio:
            portfolio_extension = os.path.splitext(portfolio.name)[1].lower()
            if not is_allowed_file(portfolio_extension, allowed_portfolio_extensions):
                return JsonResponse({'errors': 'Portfolio must be a PDF file'})
       else:
          return JsonResponse({'errors': 'Portfolio is required'})
       
        # check if user has already submitted data with the same field
       if ContractorCategory.objects.filter(partner=user, field=field).exists():
          return JsonResponse({'errors': 'You have already submitted data for this category'})
       
       # submit data to ContractorCategory
       category = ContractorCategory(partner_id=user, field_id=field, nca_id=nca)
       category.save()

        # submit data to ContractorPortfolio
       portfolio = ContractorPortfolio(category_id=category.pk, profile=portfolio)
       portfolio.save()

       response = {  'success':'Details Submitted successfully.' } 

    else:
       response = { 'errors':'Invalid Request!' }

    return JsonResponse(response)  
    
@login_required
def approve(request):
    users = CustomUser.objects.filter(is_expert=True, is_approved=False)
    for user in users:
        if PartnerMeta.objects.filter(partner=user.pk).exists():
            meta = PartnerMeta.objects.get(partner=user.pk)
            if meta.approval_doc and meta.approval_doc != "documents/none.png":
                CustomUser.objects.filter(id=user.pk).update(is_approved=True)

    messages.success(request, "Experts Approved Successfully")

    return redirect("index")


