from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from items.models import Categories, Products
from accounts.models import CustomUser,Profile, Tkeys, CompanyMeta
import json
from accounts.forms import VsignUpForm
import json, random, africastalking, re
from accounts import views
from django.views.generic import View, UpdateView
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.tokens import account_activation_token



class ActivateAccount(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            Prof = Profile.objects.get(user_id=uid)
            Prof.email_confirmed = True
            Prof.save()

            
            messages.success(request, ('Your account have been activated.'))
            return redirect('/account_verified/'+str(uid))
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('/v_failed/'+str(uid))


def e_verify(request, id):
  checks = Profile.objects.filter(user_id=id, email_confirmed=0,v_type=1)
  if checks.exists():
     template = loader.get_template('registration/verify/verify_sent.html')
     context = {
        'id': id,
        }
  
     return HttpResponse(template.render(context, request))
  else:
    messages.error(request, ('Action Not Allowed.'))
    return redirect('/login')

def vmail(request,id):
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
  
 
    messages.info(request, 'Verifification Email Sent ')
    return redirect('/e_verify/'+str(id))
 
  else:

   
   messages.error(request, 'Error Processing Your Request')
  

  return redirect('/v_failed/'+str(id))

def vfailed(request, id):
  template = loader.get_template('registration/verify/verify_failed.html')
  context = {
    'id': id,
  }
  
  return HttpResponse(template.render(context, request))

def verified(request, id):
  vsmail(request, id, 0)
  template = loader.get_template('registration/verify/verify_success.html')
  context = {
    'id': id,
  }
  
  return HttpResponse(template.render(context, request))

def v_sms(request,id):
  checks = Profile.objects.filter(user_id=id, email_confirmed=0,v_type=2)
  if checks.exists():
     user = CustomUser.objects.get(id=id)
     phone = user.phone_number
     template = loader.get_template('registration/verify/verify_sms.html')
     context = {
       'id': id,
       'phone': phone,
         }
  
     return HttpResponse(template.render(context, request))
  else:
     messages.error(request, ('Action Not Allowed.'))
     return redirect('/login')


def verify_sms(request):
  if request.method =='POST':
    a = request.POST['first']
    b = request.POST['second']
    c = request.POST['third']
    d = request.POST['fourth']
    e = request.POST['fifth']
    f = request.POST['sixth']
    id = request.POST['id']

    code = a+b+c+d+e+f
    checks = Profile.objects.filter(user_id=id, email_confirmed=0, v_type=2)
    if checks.exists():
      ichecks = Profile.objects.filter(user_id=id, v_key=code)
      if ichecks.exists():
         user = CustomUser.objects.get(id=id)
         user.is_active = True
         user.save()

         Prof = Profile.objects.get(user_id=id)
         Prof.email_confirmed = True
         Prof.save()

         messages.success(request, ('Your account have been activated.'))
         return redirect('/account_verified/'+str(id))
      else:
        messages.error(request, ('Invalid Code Provided. Kindly Re-enter The Correct Code'))
        return redirect('/v_sms/'+str(id))
    else:
            messages.warning(request, ('Validation failed, possibly because the account is already activated or your details are incorrect.'))
            return redirect('/v_failed/'+str(id))
            

def code_resend(request,id):
  checks = Profile.objects.filter(user_id=id, email_confirmed=0,v_type=2)
  if checks.exists():
      key = random.randrange(100000, 999999)
      Prof = Profile.objects.get(user_id=id)
      Prof.v_key = key
      Prof.save()

      v_resend(id, key)
      messages.success(request, ('Verification Code Re-sent.'))
      return redirect('/v_sms/'+str(id))
  else:
     messages.error(request, ('Action Not Allowed.'))
     return redirect('/login')




def v_resend(id, key):
  user = CustomUser.objects.get(id=id)
  num = user.phone_number
  phone = re.sub(r'^.', '+254', num).split(",")
  name = user.first_name
  message =  "Dear "+name+",\n Your verification code is "+str(key)+"\n Do not share it with anyone."
  sender= "GADGET_CITY"
  print(phone)
  items = Tkeys.objects.get()
  username =  items.u_name
  api_key =  items.u_key

  africastalking.initialize(username, api_key)

  sms = africastalking.SMS

  sms.send(message, phone,sender)


def number_adjust(request):
  if request.method =='POST':
    id = request.POST['id']
    phone = request.POST['phone']

    user = CustomUser.objects.get(id=id)
    user.phone_number = phone
    user.save()

    messages.success(request, ('Phone_Number Updated & Verification Code Re-sent.'))
    return redirect('/v_cresend/'+str(id))
  else:
    messages.error(request, ('Action Not Allowed.'))
    return redirect('/login')

def v_change(request,id):
    check = Profile.objects.get(user_id=id)
    type = check.v_type
    if type == '1':
       user = Profile.objects.get(user_id=id)
       user.v_type = 2
       user.save()

       messages.success(request, ('Account Verification Changed To SMS.'))
       return redirect('/v_cresend/'+str(id))
    else:
       us = Profile.objects.get(user_id=id)
       us.v_type = 1
       us.save()

       messages.success(request, ('Account Verification Changed To Mail.'))
       return redirect('/v_resend/'+str(id))
  
def e_verify(request, id):
  checks = Profile.objects.filter(user_id=id, email_confirmed=0,v_type=1)
  if checks.exists():
     template = loader.get_template('registration/verify/verify_sent.html')
     context = {
        'id': id,
        }
  
     return HttpResponse(template.render(context, request))
  else:
    messages.error(request, ('Action Not Allowed.'))
    return redirect('/login')

def vsmail(request, id, code):
    meta = CompanyMeta.objects.get(id=1)
    checks = CustomUser.objects.filter(id=id)
    if checks.exists():
        user = CustomUser.objects.get(id=id)
        first = user.first_name
        email = user.email

        c = {
            "email": email,
            "uname": first,
            "domain": meta.url,
            "site_name": meta.name,
            "protocol": meta.protocol,
        }
        if code == 0:
            subject = "Welcome To JaGedo"

            htmltemp = loader.get_template("registration/verify/welcome_email.html")

        else:
            subject = "Account Deactivated"

            htmltemp = loader.get_template("registration/verify/deactivated_email.html")

        html_content = htmltemp.render(c)
        try:
            msg = EmailMultiAlternatives(
                subject,
                html_content,
                "JaGedo" + "<" + meta.email + ">",
                [user.email],
                headers={"Reply-To": meta.email},
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except BadHeaderError:
            return HttpResponse("Invalid header found.")

        messages.info(request, " Email Sent ")

    else:
        messages.error(request, "Error Processing Your Request")
  

 
  
  
  
  
  
