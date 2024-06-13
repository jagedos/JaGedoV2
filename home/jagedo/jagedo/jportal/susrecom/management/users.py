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
from experts.models import Fields, Skills, Certs,Wdays, PartnerCerts, \
PartnerMeta, PartnerSkills, PartnerTimes, ContractorMeta
from vendors.models import Counties
import magic, os
from django.conf import settings
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required
from django.db import transaction
from management.models import UserTypes

# Create your views here.
@login_required
@manager_watch

def index(request):
  users = CustomUser.objects.filter(is_manager=True)
  roles = UserTypes.objects.all()
  counties = Counties.objects.all()
  utype=1
  
  
  template = loader.get_template('users/users.html')
  context = {
    'users': users,
    'utype': utype,
    'counties': counties,
    "roles": roles
  }
  return HttpResponse(template.render(context, request))

def is_allowed_file(file_extension, allowed_extensions):
    return file_extension in allowed_extensions

def vendors(request):
  users = CustomUser.objects.filter(is_vendor=True)
  counties = Counties.objects.all()
  utype=2
  
  
  template = loader.get_template('users/users.html')
  context = {
    'users': users,
    'utype': utype ,
    'counties': counties
  }
  return HttpResponse(template.render(context, request))


def pvendors(request):
  users = CustomUser.objects.filter(is_vendor=True,is_approved=False)
  utype=2
  
  
  template = loader.get_template('users/pending.html')
  context = {
    'users': users,
    'utype': utype
  }
  return HttpResponse(template.render(context, request))


def vdocs(request,id):
  vdocs= Vdocs.objects.filter(vendor=id).first()
  template = loader.get_template('users/vdocs.html')
  context = {
    'i': 1,
    'vdocs': vdocs,
    'ptitle': 'Vendor Documents'
  }
  return HttpResponse(template.render(context, request))
  

def customers(request):
  users = CustomUser.objects.filter(is_customer=True)
  counties = Counties.objects.all()
  utype=3
  
  
  template = loader.get_template('users/users.html')
  context = {
    'users': users,
    'utype': utype,
    'counties': counties
  }
  return HttpResponse(template.render(context, request))

@login_required
@manager_watch
def addrecord(request):
  if request.method =='POST':
    first = request.POST['first_name']
    last = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    location = request.POST['location']
    county = request.POST['county']
    nid = request.POST['national_id']
    utype = int(request.POST['utype'])
    password = make_password(request.POST['password'])
    time = datetime.now()
    if request.POST['status'] == '0':
       status = False
    else:
       status = True

    echeck = CustomUser.objects.filter(email=email)
    pcheck = CustomUser.objects.filter(phone_number=phone)
    
    if echeck.exists():
      response = {
        'errors':'Email already taken !' 
            } 
    
    elif pcheck.exists():
        response = {
        'errors':'Phone already taken !' 
            }
    else:
      if utype == 1:
        role = request.POST["usertype"]
        member = CustomUser(first_name=first, last_name=last, email=email, phone_number=phone, national_id=nid , location=location ,password=password, usertype=UserTypes.objects.get(id=role),
        date_joined=time, is_active=status, is_manager=True)
        member.save()
      elif utype == 2:
         member = CustomUser(first_name=first, last_name=last, email=email, phone_number=phone, national_id=nid , location=location ,password=password,
         date_joined=time, is_active=status, is_vendor=True)
         member.save()
      elif utype == 3:
         member = CustomUser(first_name=first, last_name=last, email=email, phone_number=phone, national_id=nid , location=location,password=password,
         date_joined=time, is_active=status, is_customer=True)
         member.save()

         

         if member.is_active == False:

            Prof = Profile.objects.get(user_id=member.pk)
            Prof.county_id = county
            Prof.location_id = county
            Prof.v_type = 1
            Prof.save()

            v_mail(request,member.pk)
         else:
           Prof = Profile.objects.get(user_id=member.pk)
           Prof.county_id = county
           Prof.location_id = county
           Prof.email_confirmed = 1
           Prof.v_type = 1
           Prof.save()

      response = {
        'success':'Data Added successfully.' 
            }
      
  else:
        response = {
        'errors':'Invalid Request!' 
            }
      
  return JsonResponse(response)



@login_required
@manager_watch
def addexpert(request):
  if request.method =='POST':
    allowed_cv_extensions = ['.pdf']
    allowed_id_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp']
    allowed_cert_extensions = ['.pdf']

    first = request.POST['first_name']
    last = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    nid = request.POST['national_id']
    approval = int(request.POST['astatus'])
    lcounty = request.POST['county']
    password = make_password(request.POST['password'])
    time = datetime.now()
    if request.POST['status'] == '0':
       status = False
    else:
       status = True
    gender = int(request.POST['gender'])
    regas = int(request.POST['reg_as'])
    yrs = int(request.POST['yrs_of_experience'])
    afield = int(request.POST['field'])
    skills = request.POST.getlist('skills')
    icv = request.FILES.get('cv')
    if icv is None:
      cv = 1
    else:
      cv = request.FILES['cv']
      cv_extension = os.path.splitext(cv.name)[1].lower()
      if not is_allowed_file(cv_extension, allowed_cv_extensions):
                return JsonResponse({'errors': 'CV must be a PDF file'})
    
    idfrontc = request.FILES.get('id_front')
    if idfrontc is None:
      idfront = 1
    else:
      idfront = request.FILES['id_front']
      idfront_extension = os.path.splitext(idfront.name)[1].lower()
      if not is_allowed_file(idfront_extension, allowed_id_extensions):
                return JsonResponse({'errors': 'Id_Front must be an image or a PDF file'})

    idbackc = request.FILES.get('id_back')
    if idbackc is None:
      idback = 1
    else:
      idback = request.FILES['id_back']
      idback_extension = os.path.splitext(idback.name)[1].lower()
      if not is_allowed_file(idback_extension, allowed_id_extensions):
                return JsonResponse({'errors': 'Id_Back must be an image or a PDF file'})

    cname = request.POST.getlist('cert_name')
    certs = request.FILES.getlist('certs')
    availability = int(request.POST['aset'])
    day = request.POST.getlist('day')
    start = request.POST.getlist('start')
    end = request.POST.getlist('end')
    loc = int(request.POST['location'])

    county= Counties.objects.get(id=loc)
    echeck = CustomUser.objects.filter(email=email)
    pcheck = CustomUser.objects.filter(phone_number=phone)

  
    # Check file extensions for certs
    for cert_file in certs:
        cert_extension = os.path.splitext(cert_file.name)[1].lower()
        if not is_allowed_file(cert_extension, allowed_cert_extensions):
                    return JsonResponse({'errors': 'Certificates must be PDF files'})
    
    if echeck.exists():
      response = {
        'errors':'Email already taken !' 
            } 
    
    elif pcheck.exists():
        response = {
        'errors':'Phone already taken !' 
            }

    elif not skills:
        response = {
        'errors':'Add atleast one skill / specialisation !' 
            }
    elif availability == 1 and not day or not start or not end:
        response = {
          'errors':'Kindly set custom availability correctly in the table provided Or set your availability to EveryDay' 
            }
    else:
         if approval == 1:
            member = CustomUser(first_name=first, last_name=last, email=email, phone_number=phone, national_id=nid, location=lcounty ,password=password,
            date_joined=time, is_active=status, is_expert=True, is_approved=True)
         else:
            member = CustomUser(first_name=first, last_name=last, email=email, phone_number=phone, national_id=nid, location=lcounty  ,password=password,
            date_joined=time, is_active=status, is_expert=True)
         member.save()

         Prf = Profile.objects.get(user_id=member.pk)
         Prf.county = county
         Prf.location = county
         Prf.save()

         partner = CustomUser.objects.get(id=member.pk)
         field =Fields.objects.get(id=afield)
         

         meta = PartnerMeta()
         meta.location=county
         meta.gender=gender
         meta.regas=regas
         meta.yrs=yrs
         meta.field=field
         meta.availability=availability
         if not cv == 1:
           meta.cv=cv
         if not idfront == 1:
           meta.idfront=idfront
         if not idback == 1:  
           meta.idback=idback
         meta.partner=partner
         meta.save()
      
        
         for s in range(len(skills)):
           pskill = skills[s]
           skil = Skills.objects.get(id=pskill)
           skill= PartnerSkills(field=field, skill=skil,partner=partner)
           skill.save()
         
         if not certs or not cname:

           none=''

         else:
           for i in range(len(cname)):
             cert_name = cname[i]
             cert_file = certs[i]
             certname = Certs.objects.get(id=cert_name)
             peps = PartnerCerts(cert=certname, doc=cert_file, partner=partner)
             peps.save()

         if availability == 1:
           for a in range(len(day)):
             day_name = day[a]
             start_time = start[a]
             end_time = end[a]
             days= Wdays.objects.get(id=day_name)
             wrk = PartnerTimes(day=days, start=start_time, end=end_time, partner=partner)
             wrk.save()
         
         Profile.objects.filter(user=partner).update(has_details=True)
         

         if member.is_active == False:

            Prof = Profile.objects.get(user_id=member.pk)
            Prof.v_type = 1
            Prof.save()

            v_mail(request,member.pk)
         else:
           Prof = Profile.objects.get(user_id=member.pk)
           Prof.email_confirmed = 1
           Prof.v_type = 1
           Prof.save()

         response = {
        'success':'Data Added successfully.' 
            }
      
  else:
    response = {
        'errors':'Invalid Request!' 
            }
      
      

  return JsonResponse(response)

@login_required
@manager_watch
@transaction.atomic
def addcontractor(request):
  if request.method =='POST':
    
    first = request.POST['first_name']
    last = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    nid = request.POST['national_id']
    approval = int(request.POST['astatus'])
    lcounty = int(request.POST['county'])
    company_name = request.POST['company_name']
    company_email = request.POST['company_email']
    company_phone = request.POST['company_phone']
    password = make_password(request.POST['password'])
    time = datetime.now()
    if request.POST['status'] == '0':
       status = False
    else:
       status = True

   
    

    
    loc = request.POST['location']

    county= Counties.objects.get(id=lcounty)
    echeck = CustomUser.objects.filter(email=email)
    pcheck = CustomUser.objects.filter(phone_number=phone)

  
    
    
    if echeck.exists():
      response = {
        'errors':'Email already taken !' 
            } 
    
    elif pcheck.exists():
        response = {
        'errors':'Phone already taken !' 
            }

   
    else:
         if approval == 1:
            member = CustomUser(first_name=first, last_name=last, email=email, phone_number=phone, national_id=nid, location=loc ,password=password,
            date_joined=time, is_active=status, is_expert=True, is_approved=True)
         else:
            member = CustomUser(first_name=first, last_name=last, email=email, phone_number=phone, national_id=nid, location=loc  ,password=password,
            date_joined=time, is_active=status, is_expert=True)
         member.save()

         Prf = Profile.objects.get(user_id=member.pk)
         Prf.county = county
         Prf.location = county
         Prf.save()

         partner = CustomUser.objects.get(id=member.pk)
         
         

         meta = PartnerMeta()
         meta.location=county
         meta.regas=3
         meta.partner=partner
         meta.save()

         cmeta = ContractorMeta()
         cmeta.company_name=company_name
         cmeta.company_email=company_email
         cmeta.company_phone=company_phone
         cmeta.partner=partner
         cmeta.save()


         if member.is_active == False:

            Prof = Profile.objects.get(user_id=member.pk)
            Prof.v_type = 1
            Prof.save()

            v_mail(request,member.pk)
         else:
           Prof = Profile.objects.get(user_id=member.pk)
           Prof.email_confirmed = 1
           Prof.v_type = 1
           Prof.save()

         response = {
        'success':'Data Added successfully.' 
            }
      
  else:
    response = {
        'errors':'Invalid Request!' 
            }
      

  return JsonResponse(response)

# update contractor
@login_required
@manager_watch
@transaction.atomic
def updatecontractor(request):
   if request.method =='POST':
        id = request.POST['chidden_id']
        first = request.POST['first_name']
        last = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        nid = request.POST['national_id']
        approval = int(request.POST['astatus'])
        lcounty = int(request.POST['county'])
        company_name = request.POST['company_name']
        company_email = request.POST['company_email']
        company_phone = request.POST['company_phone']
        passwor = request.POST['password']

        loc = request.POST['location']
        
        if request.POST['status'] == '0':
          status = False
        else:
          status = True


        echeck = CustomUser.objects.get(id=id)
        stat= echeck.is_active
        passw = echeck.password
        
        if passwor == passw :
          password = request.POST['password']

        else:
          password = make_password(request.POST['password'])


        member = CustomUser.objects.get(id=id)
        member.first_name = first
        member.last_name = last
        member.email = email
        member.phone_number = phone
        member.national_id = nid
        member.location=loc
        member.is_active = status
        member.password = password
        if approval == 1:
          member.is_approved = True
        else:
          member.is_approved = False
        member.save()

        Prf = Profile.objects.get(user_id=id)
        Prf.county_id = lcounty
        Prf.location_id= lcounty
        Prf.save()

        ContractorMeta.objects.filter(partner_id=id).update(company_name=company_name, company_email=company_email, company_phone=company_phone)

        if stat == status:
            msg = 'none'
          
        else:
            if status == False:

            
              vsmail(request,id,1)
            else:
              Prof = Profile.objects.get(user_id=id)
              Prof.email_confirmed = 1
              Prof.v_type = 1
              Prof.save()

              vsmail(request,id,0)

        response = {
            'success':'Data Updated successfully.' 
                }
        
   else:
        response = {
            'errors':'Invalid Request!' 
                }
        
   return JsonResponse(response)

   
   

def v_mail(request,id):
  meta = CompanyMeta.objects.get(id=1)
  checks = Profile.objects.filter(user_id=id, email_confirmed=0,v_type=1)
  if checks.exists():
    user = CustomUser.objects.get(id=id)
    first = user.first_name
    email = user.email
    
    subject = "Email Verification"
  
    htmltemp = loader.get_template('registration/verify/verify_email.html')
    c = {
	  "email":email,
    "uname":first,
	  'domain': meta.url,
	  'site_name': meta.name,
	  "uid": urlsafe_base64_encode(force_bytes(user.pk)),
	  'token': account_activation_token.make_token(user),
	  'protocol': meta.protocol,
					}
    html_content = htmltemp.render(c)
    try:
      msg = EmailMultiAlternatives(subject, html_content, 'JengaCart <jenga@susrecomm.co.ke>', [user.email], headers = {'Reply-To': 'jenga@susrecomm.co.ke'})
      msg.attach_alternative(html_content, "text/html")
      msg.send()
    except BadHeaderError:
            return HttpResponse('Invalid header found.')
  
 
    messages.info( request,'Verifification Email Sent ')
    
 
  else:

   
   messages.error( request, 'Error Processing Your Request')
  

  
@login_required
@manager_watch
def edita(request, id):
  products = CustomUser.objects.get(id=id)
  prof = Profile.objects.get(user_id=id)
  mymember = model_to_dict(products)

  response = {
    'data': mymember ,
    'county': prof.county.id,

  }

  return JsonResponse(response, safe=False)
@login_required
@manager_watch
def updaterecord(request):
 if request.method =='POST':
    first = request.POST['first_name']
    last = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    nid = request.POST['national_id']
    location = request.POST['location']
    county = request.POST['county']
    usertype = request.POST["usertype"]
    passwor = request.POST['password']
    id = request.POST['hidden_id']

    
    if request.POST['status'] == '0':
       status = False
    else:
       status = True

    echeck = CustomUser.objects.get(id=id)
    stat= echeck.is_active
    passw = echeck.password
    
    if passwor == passw :
      password = request.POST['password']

    else:
      password = make_password(request.POST['password'])

    
    member = CustomUser.objects.get(id=id)
    member.first_name = first
    member.last_name = last
    member.email = email
    member.phone_number = phone
    member.national_id = nid
    member.usertype_id = usertype
    member.location = location
    member.is_active = status
    member.password = password
    member.save()

    Prf = Profile.objects.get(user_id=id)
    Prf.county_id = county
    Prf.location_id = county
    Prf.save()

    if stat == status:
        msg = 'none'
       
    else:
        if status == False:

        
         vsmail(request,id,1)
        else:
           Prof = Profile.objects.get(user_id=id)
           Prof.email_confirmed = 1
           Prof.v_type = 1
           Prof.save()

           vsmail(request,id,0)

    response = {
        'success':'Data Updated successfully.' 
            }
      
 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)
 
@login_required
@manager_watch
def delete(request, id):
    dets = CustomUser.objects.get(id=id)
    user_type = dets.usertype.pk
    if user_type == 1:
        memb = Profile.objects.get(user_id=id)
        memb.delete()

        member = CustomUser.objects.get(id=id)
        member.delete()

        response = {"success": "Data Deleted successfully."}
    else:
        response = {"errors": "You Do Not Have Permission To Perform This Action !"}

    return JsonResponse(response)


@login_required
@manager_watch
def uapp(request, id):
  

  member = CustomUser.objects.get(id=id)
  member.is_approved= True
  member.save()
 
  
  response = {
        'success':'Vendor Approved successfully.' 
            }
  return JsonResponse(response)

def vsmail(request,id,code):
  meta = CompanyMeta.objects.get(id=1)
  checks = CustomUser.objects.filter(id=id)
  if checks.exists():
    user = CustomUser.objects.get(id=id)
    first = user.first_name
    email = user.email

    c = {
	    "email":email,
      "uname":first,
	    'domain': meta.url,
	    'site_name': meta.name,
	    'protocol': meta.protocol,
					}

    if code == 0:
      subject = "Welcome To JengaCart"
  
      htmltemp = loader.get_template('registration/verify/welcome_email.html')
      
    else:
      subject = "Account Deactivated"
  
      htmltemp = loader.get_template('registration/verify/deactivated_email.html')
     

    html_content = htmltemp.render(c)
    try:
      msg = EmailMultiAlternatives(subject, html_content, 'JengaCart <jenga@susrecomm.co.ke>', [user.email], headers = {'Reply-To': 'jenga@susrecomm.co.ke'})
      msg.attach_alternative(html_content, "text/html")
      msg.send()
    except BadHeaderError:
            return HttpResponse('Invalid header found.')
  
 
    messages.info(request, ' Email Sent ')
    
 
  else:

   
   messages.error(request, 'Error Processing Your Request')


@login_required
@manager_watch
def profile(request):
  template = loader.get_template('users/profile.html')
  context = {
    'i': 1,
  }
  return HttpResponse(template.render(context, request))
  
@login_required
@manager_watch
def updateprofile(request):
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
@manager_watch
def updateexperts(request):
 if request.method =='POST':
    first = request.POST['first_name']
    last = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    nid = request.POST['national_id']
    gender = int(request.POST['gender'])
    regas = int(request.POST['reg_as'])
    yrs = int(request.POST['yrs_of_experience'])
    approval = int(request.POST['astatus'])
    loc = int(request.POST['location'])
    passwor = request.POST['password']
    id = request.POST['hidden_id']
    lcounty= request.POST['county']

    
    county= Counties.objects.get(id=loc)

    
    if request.POST['status'] == '0':
       status = False
    else:
       status = True

    echeck = CustomUser.objects.get(id=id)
    stat= echeck.is_active
    passw = echeck.password
    
    if passwor == passw :
      password = request.POST['password']

    else:
      password = make_password(request.POST['password'])

    
    member = CustomUser.objects.get(id=id)
    member.first_name = first
    member.last_name = last
    member.email = email
    member.phone_number = phone
    member.national_id = nid
    member.location=lcounty
    member.is_active = status
    member.password = password
    if approval == 1:
      member.is_approved = True
    else:
      member.is_approved = False
    member.save()

    Prf = Profile.objects.get(user_id=id)
    Prf.county_id = loc
    Prf.location_id= loc
    Prf.save()
    
    checker = PartnerMeta.objects.filter(partner=id)

    if checker.exists():
            checker.update(gender=gender, regas=regas, yrs=yrs, location=county)
    else:
            PartnerMeta.objects.create(
                gender=gender, regas=regas, yrs=yrs, location=county, partner=member
            )

    if stat == status:
        msg = 'none'
       
    else:
        if status == False:

        
         vsmail(request,id,1)
        else:
           Prof = Profile.objects.get(user_id=id)
           Prof.email_confirmed = 1
           Prof.v_type = 1
           Prof.save()

           vsmail(request,id,0)

    response = {
        'success':'Data Updated successfully.' 
            }
      
 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)

@login_required
@manager_watch
def vuploads(request, id):
   dts = Vdocs.objects.filter(vendor=id)
   if dts.exists():

     dets = Vdocs.objects.get(vendor=id)

     cdets= CompanyMeta.objects.get(id=1)

     
   
     img =' <table width="100%" class="table table-bordered"> \
      <thead> \
    <tr> \
     <th>Title</th> \
      <th>Action</th> \
        </tr> </thead>\
          <tbody> \
             '
     img+='<tbody> \
       <tr> \
        <td>Id_Front</td> \
        <td><span class="view badge bg-primary" id="0.'+str(dets.pk)+'">View</span>&nbsp;&nbsp;<a href="/media/'+str(dets.idfront)+'" class=" badge bg-info" id="0">Download</a></td> \
      </tr> \
      <tr> \
        <td>Id_Back</td> \
        <td><span class="view badge bg-primary" id="1.'+str(dets.pk)+'">View</span>&nbsp;&nbsp;<a href="/media/'+str(dets.idback)+'" class=" badge bg-info" id="1">Download</a></td> \
      </tr> \
      <tr> \
        <td>Business_Registration_Cerificate</td> \
        <td><span class="view badge bg-primary" id="2.'+str(dets.pk)+'">View</span>&nbsp;&nbsp;<a href="/media/'+str(dets.bizreg)+'" class="badge bg-info" id="2">Download</a></td> \
      </tr> \
      <tr> \
        <td>Tax_Compliance_Certificate</td> \
        <td><span class="view badge bg-primary" id="3.'+str(dets.pk)+'">View</span>&nbsp;&nbsp;<a href="/media/'+str(dets.taxcomp)+'" class="badge bg-info" id="3">Download</a></td> \
      </tr> \
         </tbody> \
              </table> '
   
   else:
     img='<i><b>No Images Uploaded!</b></i>'



 
  
      
      

   parameters = { 'media': img }
   response = parameters

   return JsonResponse(response)

@login_required
@manager_watch
def uviews(request, id):
  part1 = id.split(".",1)[0]
  part2 = id.split(".",1)[1]
  uid = int(part2)
  type = int(part1)


  dets = Vdocs.objects.get(id=uid)
  mymember = model_to_dict(dets)

  if type == 0:
    path=dets.idfront
  elif type == 1:
    path=dets.idback
  elif type == 2:
    path=dets.bizreg
  elif type == 3:
    path=dets.taxcomp

  cdets= CompanyMeta.objects.get(id=1)

 
  media = '<embed  src="http://docs.google.com/viewer?url='+str(cdets.protocol)+'://'+str(cdets.url)+'/media/'+str(path)+'&embedded=true" style="margin:0 auto; width:800px; height:800px;" frameborder="0"></iframe>'
  
      
      

  parameters = { 'media': media }
  response = parameters

  return JsonResponse(response)