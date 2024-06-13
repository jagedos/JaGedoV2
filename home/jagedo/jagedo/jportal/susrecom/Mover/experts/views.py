from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from core.models import OrderCarts,Orders,jobs,Pcategories
from items.models import Categories, Products
from django.forms.models import model_to_dict
from vendors.models import Counties
from accounts.models import CustomUser, Vdocs, Profile
from experts.models import Fields, Skills, Certs,Wdays, PartnerCerts, PartnerMeta, PartnerSkills, PartnerTimes, Quotations, NcaFields, ContractorCategory, ContractorPortfolio, ContractorMeta
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.db.models import Sum, Count, Q
from accounts.decorators import authentication_not_required, customer_watch, manager_watch,logistics_watch, experts_watch
from django.contrib.auth.decorators import login_required
from management.models import Counties, LegalDocuments, LegalDocumentTypes
from django.db import transaction
import os

# Create your views here.
@login_required
@experts_watch
def index(request):
  fundi=request.user.id
  skils = PartnerSkills.objects.filter(partner=request.user.id).values_list('skill', flat=True)
  vdcs= Profile.objects.get(user=request.user.id)
  actives = Quotations.objects.filter(expert=request.user.id, is_selected=True,is_approved=True, is_completed=False, is_rejected=False).order_by('-id')
  ldocs = LegalDocuments.objects.filter(type__is_partner=True)
  m_data = PartnerMeta.objects.filter(partner=request.user.id).first()
  


  fields= Fields.objects.all()
  certs= Certs.objects.all()
  img=''
  for c in certs:
    img+='<option value="'+str(c.pk)+'">'+ str(c.name) +'</option>'

  days= Wdays.objects.filter(status=True)
  dys=''
  for d in days:
    dys+='<option value="'+str(d.pk)+'">'+ str(d.name) +'</option>'

  locs= Counties.objects.all()

  acts = jobs.objects.filter(skill__in=skils,status__lte=3).order_by('-id')[:6]
  

  template = loader.get_template('expdash.html')
  context = {
    'products': 1,
    'vdocs' : vdcs,
    'fields' : fields,
    'certs' : img,
    'days' : dys,
    'locs' : locs,
    'gigs' : acts,
    'acts': actives,
    'ldocs': ldocs,
    'm_data': m_data,


  }
  return HttpResponse(template.render(context, request))

@login_required
@experts_watch
@transaction.atomic
def contractor_meta(request):
  fundi=request.user.id
  nca = NcaFields.objects.all()
  m_data = PartnerMeta.objects.filter(partner=request.user.id).first()
  check = ContractorCategory.objects.prefetch_related('contractorportfolio_set').filter(partner=fundi)
  


  fields= Fields.objects.all().exclude(id=5)
  
  

  template = loader.get_template('meta/cmeta_data.html')
  context = {
    'nca': nca,
    'fields' : fields,
    'm_data': m_data,
    'contractor': fundi,
    'check': check,


  }
  return HttpResponse(template.render(context, request))

# add contractor company details
@login_required
@experts_watch
@transaction.atomic
def addcontractorcompany(request):
    # submit data to ContractorCategory and ContractorPortfolio
      if request.method =='POST':
        user = request.user.id
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
@experts_watch
def addcontractormeta(request):
   # submit data to ContractorCategory and ContractorPortfolio
    if request.method =='POST':
       user = request.user.id
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
       

# delete contractor category and portfolio
@login_required
def deletecontractormeta(request):
  if request.method =='POST':
    id = request.POST['id']
    ContractorCategory.objects.filter(id=id).delete()
    ContractorPortfolio.objects.filter(category=id).delete()
    response = {  'success':'Data Deleted successfully.' } 

  else:
    response = { 'errors':'Invalid Request!' }

  return JsonResponse(response)

       


       
       
  
  


@login_required
@experts_watch
def profile(request):
  fundi = request.user.id
  meta = PartnerMeta.objects.filter(partner=request.user.id)
  mdet = meta.first()
  if not mdet.regas == 3:
      locs = Counties.objects.all()
      skills = PartnerSkills.objects.filter(partner=request.user.id)
      fields= Fields.objects.all().exclude(id=mdet.field.id)
      docs= PartnerCerts.objects.filter(partner=request.user.id)
      times= PartnerTimes.objects.filter(partner=request.user.id)
      certs= Certs.objects.all()
      img=''
      for c in certs:
        img+='<option value="'+str(c.pk)+'">'+ str(c.name) +'</option>'

      days= Wdays.objects.filter(status=True)
      dys=''
      for d in days:
        dys+='<option value="'+str(d.pk)+'">'+ str(d.name) +'</option>'

      template = loader.get_template('meta/profile.html')
      context = {
        'metas': meta ,
        'locs' : locs ,
        'skills' : skills,
        'fields' : fields,
        'docs' : docs,
        'certs' : img ,
        'times' : times,
        'days' : dys,
        'mdet' : mdet
      }
  else:
    contractor = ContractorMeta.objects.filter(partner=request.user.id).first()
    cats = ContractorCategory.objects.prefetch_related('contractorportfolio_set').filter(partner=request.user.id)
    nca = NcaFields.objects.all()
    fields= Fields.objects.all().exclude(id=5)


    template = loader.get_template('meta/cmeta_profile.html')
    context = {
      'metas': meta ,
      'mdet' : mdet,
      'contractor': contractor,
      'cats': cats,
      'nca': nca,
      'fields': fields,
      'fundi': fundi
    }
  return HttpResponse(template.render(context, request))

@login_required
@experts_watch
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
def getskills(request, id):
  mymember = Skills.objects.filter(field=id)
  

  img=' <select class=" form-control select2" name="skills" id="skills" required="true"  style="width: 100%;"> \
      <option selected="selected" disabled value="">Select_A_Skill</option>\
             '
  for pic in mymember:
      img+='<option value="'+str(pic.pk)+'">'+ str(pic.name) +'</option>'

  img+='</select>'
        
      
  parameters = { 'img': img, }
  response = parameters

  return JsonResponse(response)


@login_required
def getskillsx(request, id):
  part1 = id.split(".",1)[0]
  part2 = id.split(".",1)[1]
  fid = str(part1)
  sid = int(part2)

  mymember = Skills.objects.filter(field=sid)
  

  img=' <select class=" form-control select2" name="skills" id="skills" required="true"  style="width: 100%;"> \
      <option selected="selected" disabled value="">Select_A_Skill</option>\
             '
  for pic in mymember:
      img+='<option value="'+str(pic.pk)+'">'+ str(pic.name) +'</option>'

  img+='</select>'
        
      
  parameters = { 'img': img, 'fid': fid }
  response = parameters

  return JsonResponse(response)

def is_allowed_file(file_extension, allowed_extensions):
    return file_extension in allowed_extensions


@login_required
@experts_watch
def storedetails(request):
 if request.method =='POST':
    allowed_cv_extensions = ['.pdf']
    allowed_id_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp']
    allowed_cert_extensions = ['.pdf']

    gender = int(request.POST['gender'])
    regas = int(request.POST['reg_as'])
    yrs = int(request.POST['yrs_of_experience'])
    afield = int(request.POST['field'])
    skills = request.POST.getlist('skills')
    # check if cv is uploaded
    if 'cv' in request.FILES:
      cv = request.FILES['cv']
    else:
      cv = None
    idfront = request.FILES['id_front']
    idback = request.FILES['id_back']
    cname = request.POST.getlist('cert_name')
    certs = request.FILES.getlist('certs')
    availability = int(request.POST['aset'])
    day = request.POST.getlist('day')
    start = request.POST.getlist('start')
    end = request.POST.getlist('end')
    loc = int(request.POST['location'])
    uid = request.user.id


    # Check file extensions for CV, idfront, idback
    if not cv is None:
      cv_extension = os.path.splitext(cv.name)[1].lower()
      if not is_allowed_file(cv_extension, allowed_cv_extensions):
                  return JsonResponse({'errors': 'CV must be a PDF file'})

    idfront_extension = os.path.splitext(idfront.name)[1].lower()
    if not is_allowed_file(idfront_extension, allowed_id_extensions):
                return JsonResponse({'errors': 'Id_Front must be an image or a PDF file'})

    idback_extension = os.path.splitext(idback.name)[1].lower()
    if not is_allowed_file(idback_extension, allowed_id_extensions):
                return JsonResponse({'errors': 'Id_Back must be an image or a PDF file'})

    # Check file extensions for certs
    for cert_file in certs:
        cert_extension = os.path.splitext(cert_file.name)[1].lower()
        if not is_allowed_file(cert_extension, allowed_cert_extensions):
                    return JsonResponse({'errors': 'Certificates must be PDF files'})

    county= Counties.objects.get(id=loc)

    if regas == 1:


      # if not cname or not certs:
      #   response = {
      #     'errors':'Kindly Upload Atleast One Academic Or Practice certificate !.' 
      #       }
      if availability == 1 and not day or not start or not end:
        response = {
          'errors':'Kindly set custom availability correctly in the table provided Or set your availability to EveryDay' 
            }

      else:
        field =Fields.objects.get(id=afield)
        partner = CustomUser.objects.get(id=uid)
        # check if cv is empty
        if not cv is None:
           meta = PartnerMeta(location=county,gender=gender, regas=regas, yrs=yrs, field=field, availability=availability, cv=cv, idfront=idfront, idback=idback, partner=partner)
           meta.save()
        else:
           meta = PartnerMeta(location=county,gender=gender, regas=regas, yrs=yrs, field=field, availability=availability, cv=cv, idfront=idfront, idback=idback, partner=partner)
           meta.save()
           
           
      
        
        for s in range(len(skills)):
          pskill = skills[s]
          skil = Skills.objects.get(id=pskill)
          skill= PartnerSkills(field=field, skill=skil,partner=partner)
          skill.save()
          
        # check if cname and certs are empty
        if cname and certs:
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
        response = {
        'success':'Details Updated successfully.' 
            }

    else:
      if availability == 1 and not day or not start or not end:
        response = {
          'errors':'Kindly set custom availability correctly in the table provided Or set your availability to EveryDay' 
            }

      else:
        field =Fields.objects.get(id=afield)
        partner = CustomUser.objects.get(id=uid)
        
        meta = PartnerMeta(location=county, gender=gender, regas=regas, yrs=yrs, field=field, availability=availability, cv=cv, idfront=idfront, idback=idback, partner=partner)
        meta.save()


        for s in range(len(skills)):
          pskill = skills[s]
          skil = Skills.objects.get(id=pskill)
          skill= PartnerSkills(field=field, skill=skil,partner=partner)
          skill.save()

        if not cname or not certs:
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
        response = {
        'success':'Details Updated successfully.' 
            }

 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)



@login_required
def medit(request, id):
  products = PartnerMeta.objects.get(partner=id)


  parameters = { 'id': products.pk,
                 'gender': products.gender,
                 'yrs': products.yrs,
                 'location': products.location.id,
                 'regas': products.regas,
                 'cv': str(products.cv),
                 'idfront': str(products.idfront),
                 'idback': str(products.idback),
                 'approval_doc': str(products.approval_doc),

   }
  response = parameters

  return JsonResponse(response)


@login_required
def contractor_edit(request, id):
  products = ContractorMeta.objects.get(id=id)


  parameters = { 'id': products.pk,
                 'company_name': products.company_name,
                 'company_email': products.company_email,
                 'company_phone': products.company_phone,
                 'company_cert': str(products.company_cert),
                 'pin_cert': str(products.pin_cert),
                 'business_permit': str(products.business_permit),
                 'company_profile': str(products.company_profile),

   }
  response = parameters

  return JsonResponse(response)

# update contractor company details
def updatecontractor_meta(request):
    if request.method =='POST':
        id = request.POST['chidden_id']
        company_name = request.POST['company_name']
        company_email = request.POST['company_email']
        company_phone = request.POST['company_phone']
        company_certificate = request.FILES.get('company_certificate')
        pin_cerfiticate = request.FILES.get('pin_certificate')
        business_permit = request.FILES.get('business_permit')
        company_profile = request.FILES.get('company_profile')
        allowed_certs = ['.pdf']
        # check if company_certificate is empty
        if not company_certificate is None:
              company_certificate_extension = os.path.splitext(company_certificate.name)[1].lower()
              if not is_allowed_file(company_certificate_extension, allowed_certs):
                  return JsonResponse({'errors': 'Company Certificate must be a PDF file'})
        
        

        # check if pin_cerfiticate is empty
        if not pin_cerfiticate is None:
              pin_cerfiticate_extension = os.path.splitext(pin_cerfiticate.name)[1].lower()
              if not is_allowed_file(pin_cerfiticate_extension, allowed_certs):
                  return JsonResponse({'errors': 'PIN Certificate must be a PDF file'})
       
        # check if business_permit is empty
        if not business_permit is None:
              business_permit_extension = os.path.splitext(business_permit.name)[1].lower()
              if not is_allowed_file(business_permit_extension, allowed_certs):
                  return JsonResponse({'errors': 'Business Permit must be a PDF file'})
        
        
        # check if company_profile is empty
        if not company_profile is None:
              company_profile_extension = os.path.splitext(company_profile.name)[1].lower()
              if not is_allowed_file(company_profile_extension, allowed_certs):
                  return JsonResponse({'errors': 'Company Profile must be a PDF file'})
        
        update = ContractorMeta.objects.get(id=id)
        update.company_name = company_name
        update.company_email = company_email
        update.company_phone = company_phone

        if not company_certificate is None:
          update.company_cert = company_certificate

        if not pin_cerfiticate is None:
          update.pin_cert = pin_cerfiticate

        if not business_permit is None:
          update.business_permit = business_permit

        if not company_profile is None:
          update.company_profile = company_profile

        update.save()
        

       
        response = {  'success':'Details Updated successfully.' } 
  
    else:
        response = { 'errors':'Invalid Request!' }
  
    return JsonResponse(response)
      




@login_required
@experts_watch
def editmeta(request):
    if request.method == 'POST':
        allowed_cv_extensions = ['.pdf']
        allowed_id_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp']

        gender = int(request.POST['gender'])
        regas = int(request.POST['reg_as'])
        yrs = int(request.POST['yrs_of_experience'])
        loc = int(request.POST['location'])

        icv = request.FILES.get('cv')
        cv = 1 if icv is None else request.FILES['cv']

        idfrontc = request.FILES.get('id_front')
        idfront = 1 if idfrontc is None else request.FILES['id_front']

        idbackc = request.FILES.get('id_back')
        idback = 1 if idbackc is None else request.FILES['id_back']

        uid = request.user.id
        county = Counties.objects.get(id=loc)

        check = PartnerMeta.objects.get(id=request.POST['hidden_id'])
        check.gender = gender
        check.regas = regas
        check.yrs = yrs
        check.location = county

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
def sedit(request, id):
  
  products = PartnerSkills.objects.get(id=id)
  skills = model_to_dict(products)


  mymember = Skills.objects.filter(field=products.field.id)
  

  img='<select class="form-control " name="skill" id="skill" ><option selected="selected" disabled value="">Select_Your_Skill</option>'
  for pic in mymember:
      img+='<option value="'+str(pic.pk)+'">'+ str(pic.name) +'</option>'

  img+='</select>'


  parameters = { 'skills': skills,
                 'askills': img,
   }
  response = parameters

  return JsonResponse(response)



@login_required
def editskill(request):
 if request.method =='POST':
    sk = int(request.POST['skill'])
    
    skill= Skills.objects.get(id=sk)
    
    check=PartnerSkills.objects.get(id = request.POST['shidden_id'])
    check.skill= skill
    check.save()


    response = {
        'success':'Details Updated successfully.' 
            }

 else:
    response = {
        'errors':'Invalid Request!' 
            }

 return JsonResponse(response)


@login_required
@experts_watch
def changeskill(request):
 if request.method =='POST':
    afield = int(request.POST['field'])
    skills = request.POST.getlist('skills')
    uid = request.user.id
    
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
@experts_watch
def addcerts(request):
    if request.method == 'POST':
        allowed_extensions = ['.pdf']
        
        cname = request.POST.getlist('cert_name')
        certs = request.FILES.getlist('certs')
        uid = int(request.user.id)

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


def delete(request, id):
  
  member = PartnerCerts.objects.get(id=id).delete()
  
 
  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)


@login_required
@experts_watch
def addtimes(request):
 if request.method =='POST':
    availability = int(request.POST['aset'])
    day = request.POST.getlist('day')
    start = request.POST.getlist('start')
    end = request.POST.getlist('end')
    uid = request.user.id
    
    
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

def tdelete(request, id):
  
  PartnerTimes.objects.get(id=id).delete()
  
 
  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)
