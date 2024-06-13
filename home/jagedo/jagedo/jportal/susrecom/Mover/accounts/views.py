from tabnanny import check
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from django.views.generic import View, UpdateView
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from management.models import Counties
from accounts.models import CustomUser,Profile , Tkeys, CompanyMeta
import json, random, africastalking, re
from accounts.forms import VsignUpForm, CsignUpForm, DsignUpForm, EsignUpForm
from items.models import Categories
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from accounts.tokens import account_activation_token
from management.models import LegalDocuments, LegalDocumentTypes
from experts.models import PartnerMeta



# Create your views here.
def index(request):
  company =  CompanyMeta.objects.get(id=1)
  docs = LegalDocuments.objects.filter(type__is_global=True)
  cats =  Categories.objects.all().values()
  form_class = VsignUpForm
  template = loader.get_template('registration/vreg.html')
  context = {
    'cats': cats,
    'form_class': form_class,
    'company': company,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))

def cindex(request):
  company =  CompanyMeta.objects.get(id=1)
  docs = LegalDocuments.objects.filter(type__is_global=True)
  cats =  Categories.objects.all().values()
  form_class = CsignUpForm
  template = loader.get_template('registration/creg.html')
  context = {
    'cats': cats,
    'form_class': form_class,
    'company': company,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))

def dindex(request):
  docs = LegalDocuments.objects.filter(type__is_global=True)
  cats =  Categories.objects.all().values()
  form_class = DsignUpForm
  template = loader.get_template('registration/dreg.html')
  context = {
    'cats': cats,
    'form_class': form_class,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))

def eindex(request):
  company =  CompanyMeta.objects.get(id=1)
  docs = LegalDocuments.objects.filter(type__is_global=True)
  cats =  Categories.objects.all().values()
  form_class = EsignUpForm
  template = loader.get_template('registration/ereg.html')
  context = {
    'cats': cats,
    'form_class': form_class,
    'company': company,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))


def coindex(request):
  docs = LegalDocuments.objects.filter(type__is_global=True)
  company =  CompanyMeta.objects.get(id=1)
  cats =  Categories.objects.all().values()
  form_class = EsignUpForm
  template = loader.get_template('registration/coreg.html')
  context = {
    'cats': cats,
    'form_class': form_class,
    'company': company,
    'docs': docs,
  }
  return HttpResponse(template.render(context, request))

def register(request):
 meta = CompanyMeta.objects.get(id=1)

 form  = VsignUpForm(request.POST)

 if form.is_valid():
  user = form.save()
  user.is_active = False # Deactivate account till it is confirmed
  user.save()

  type = request.POST['account_verify']
  county = request.POST.get('county', None)

  Prof = Profile.objects.get(user_id=user.pk)
  Prof.v_type = type
  Prof.county_id = county
  Prof.location_id = county
  Prof.save()


  if Prof.v_type == '1':
     first = form.cleaned_data.get('first_name')
     email = form.cleaned_data.get('email')
     a = CustomUser.objects.get(email=email)
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
        msg = EmailMultiAlternatives(subject, html_content, 'JaGedo <alerts@jagedo.co.ke>', [user.email], headers = {'Reply-To': 'alerts@jagedo.co.ke'})
        msg.attach_alternative(html_content, "text/html")
        msg.send()
     except BadHeaderError:
            return HttpResponse('Invalid header found.')
  
 
     messages.info(request, 'Verifification Email Sent ')
     return redirect('/e_verify/'+str(a.id))
  else:
    key = random.randrange(100000, 999999)
    Prof = Profile.objects.get(user_id=user.pk)
    Prof.v_key = key
    Prof.save()

    v_send(user.pk, key)
    return redirect('/v_sms/'+str(user.pk))
  
 
 else:
  
  print('Form is not valid')
  messages.error(request, 'Error Processing Your Request')
  context = {'form_class': form}

 return render(request, 'registration/vreg.html', context)

def cregister(request):
 meta = CompanyMeta.objects.get(id=1)

 form  = CsignUpForm(request.POST)

 if form.is_valid():
  user = form.save()
  user.is_active = False # Deactivate account till it is confirmed
  user.save()

  type = request.POST['account_verify']
  county = request.POST.get('county', None)

  Prof = Profile.objects.get(user_id=user.pk)
  Prof.v_type = type
  Prof.county_id = county
  Prof.location_id = county
  Prof.save()

  if Prof.v_type == '1':
     first = form.cleaned_data.get('first_name')
     email = form.cleaned_data.get('email')
     a = CustomUser.objects.get(email=email)
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
        msg = EmailMultiAlternatives(subject, html_content, 'JaGedo <alerts@jagedo.co.ke>', [user.email], headers = {'Reply-To': 'alerts@jagedo.co.ke'})
        msg.attach_alternative(html_content, "text/html")
        msg.send()
     except BadHeaderError:
            return HttpResponse('Invalid header found.')
  
 
     messages.info(request, 'Verifification Email Sent ')
     return redirect('/e_verify/'+str(a.id))
  else:
    key = random.randrange(100000, 999999)
    Prof = Profile.objects.get(user_id=user.pk)
    Prof.v_key = key
    Prof.save()

    v_send(user.pk, key)
    return redirect('/v_sms/'+str(user.pk))
  
 
 else:
  
  print('Form is not valid')
  messages.error(request, 'Error Processing Your Request')
  context = {'form_class': form}

 return render(request, 'registration/creg.html', context)


def dregister(request):
 meta = CompanyMeta.objects.get(id=1)

 form  = DsignUpForm(request.POST)

 if form.is_valid():
  user = form.save()
  user.is_active = False # Deactivate account till it is confirmed
  user.save()

  type = request.POST['account_verify']

  Prof = Profile.objects.get(user_id=user.pk)
  Prof.v_type = type
  Prof.save()

  if Prof.v_type == '1':
     first = form.cleaned_data.get('first_name')
     email = form.cleaned_data.get('email')
     a = CustomUser.objects.get(email=email)
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
        msg = EmailMultiAlternatives(subject, html_content, 'JaGedo <alerts@jagedo.co.ke>', [user.email], headers = {'Reply-To': 'alerts@jagedo.co.ke'})
        msg.attach_alternative(html_content, "text/html")
        msg.send()
     except BadHeaderError:
            return HttpResponse('Invalid header found.')
  
 
     messages.info(request, 'Verifification Email Sent ')
     return redirect('/e_verify/'+str(a.id))
  else:
    key = random.randrange(100000, 999999)
    Prof = Profile.objects.get(user_id=user.pk)
    Prof.v_key = key
    Prof.save()

    v_send(user.pk, key)
    return redirect('/v_sms/'+str(user.pk))
  
 
 else:
  print(form.errors.as_data())
  #print('Form is not valid')
  messages.error(request, 'Error Processing Your Request')
  context = {'form_class': form}

 return render(request, 'registration/dreg.html', context)



def eregister(request):
 meta = CompanyMeta.objects.get(id=1)

 form  = EsignUpForm(request.POST)

 if form.is_valid():
  user = form.save()
  user.is_active = False # Deactivate account till it is confirmed
  user.save()


  type = request.POST['account_verify']
  county = request.POST.get('county', None)

  Prof = Profile.objects.get(user_id=user.pk)
  Prof.v_type = type
  Prof.county_id = county
  Prof.location_id = county
  Prof.save()

  if request.POST['is_contractor'] == '1':
      mta = PartnerMeta()
      mta.location_id=county
      mta.regas = 3
      mta.partner_id=user.pk
      mta.save()

  if Prof.v_type == '1':
     first = form.cleaned_data.get('first_name')
     email = form.cleaned_data.get('email')
     a = CustomUser.objects.get(email=email)
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
        msg = EmailMultiAlternatives(subject, html_content, 'JaGedo <alerts@jagedo.co.ke>', [user.email], headers = {'Reply-To': 'alerts@jagedo.co.ke'})
        msg.attach_alternative(html_content, "text/html")
        msg.send()
     except BadHeaderError:
            return HttpResponse('Invalid header found.')
  
 
     messages.info(request, 'Verifification Email Sent ')
     return redirect('/e_verify/'+str(a.id))
  else:
    key = random.randrange(100000, 999999)
    Prof = Profile.objects.get(user_id=user.pk)
    Prof.v_key = key
    Prof.save()

    v_send(user.pk, key)
    return redirect('/v_sms/'+str(user.pk))
  
 
 else:
  print(form.errors.as_data())
  #print('Form is not valid')
  messages.error(request, 'Error Processing Your Request')
  context = {'form_class': form}

 return render(request, 'registration/ereg.html', context)

class LoginFormView(SuccessMessageMixin, LoginView):
     template_name = 'registration/login.html'
     success_url = '/accs/lswitch/'
     success_message = "You were successfully logged in"

# def show_message(sender, user, request, **kwargs):
#     # whatever...
#     messages.info(request, 'You have logged out successfully.')

# user_logged_out.connect(show_message)

def logout_view(request):
    if request.user.is_customer:
      url='/'
    else:
      url='login'

    logout(request)
    messages.info(request, 'You have logged out successfully.')
    return redirect(url)

def login_auth(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        err_code = request.session.pop('login_error', None)
        
        if user and not user.is_active:
            check = Profile.objects.get(user=user.pk)
            if check.email_confirmed:
                messages.error(request, 'Sorry, your account is deactivated.')
                return redirect('/login/')
            else:
                if check.v_type == '1':
                    return redirect('/e_verify/' + str(user.id))
                else:
                    return redirect('/v_sms/' + str(user.id))
        elif user and user.is_active:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('/accs/lswitch/')
        else:
            if err_code == 'username':
                messages.error(request, 'Invalid email/phone number. Try again.')
            elif err_code == 'password':
                messages.error(request, 'Invalid password. Try again.')
            else:
                messages.error(request, 'Invalid login credentials. Try again.')
            return redirect('/login/')
    else:
        messages.error(request, 'Action not allowed.')
        return redirect('/login/')


@login_required
def logswitch(request):
 
  if request.user.is_customer:    
       
       return redirect('/')

  elif request.user.is_manager:
         
           return redirect('/mans/')
           
  elif request.user.is_vendor:
                
       return redirect('/vendors/')

  elif request.user.is_delivery:
                
       return redirect('/logistics/')
  
  elif request.user.is_expert:
       
       return redirect('/fundis/')

  else:

    return redirect('/logout')

      
  

def v_send(id, key):
  user = CustomUser.objects.get(id=id)
  num = user.phone_number
  phone = re.sub(r'^.', '+254', num).split(",")
  name = user.first_name
  message =  "Dear "+name+",\n Your verification code is "+str(key)+"\n Do not share it with anyone."
  items = Tkeys.objects.get()
  username =  items.u_name
  api_key =  items.u_key
  sender= "SUSRECOMM"


  africastalking.initialize(username, api_key)

  sms = africastalking.SMS

  sms.send(message, phone, sender)


# def on_finish(error, response):
#     if error is not None:
#         raise error
#     print(response)

# def sms(request):
#   items = Tkeys.objects.get()
#   username =  items.u_name
#   api_key =  items.u_key
#   message =  "Hello Message!"
#   phone =  ["+254719757227"]
#   sender= "GADGET_CITY"


#   africastalking.initialize(username, api_key)


#   # Initialize a service e.g. SMS
#   sms = africastalking.SMS


#   # Use the service synchronously
#   sms.send(message, phone,sender, callback=on_finish)
  
 
#   messages.info(request, 'Message Sent ')
#   return redirect('/')