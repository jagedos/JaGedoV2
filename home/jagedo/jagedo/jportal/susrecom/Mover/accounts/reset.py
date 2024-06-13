from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import PasswordResetForm
from accounts.models import  CustomUser, CompanyMeta
from django.template import loader
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages





# def password_reset_request(request):
# 	if request.method == "POST":
# 		password_reset_form = PasswordResetForm(request.POST)
# 		if password_reset_form.is_valid():
# 			data = password_reset_form.cleaned_data['email']
# 			associated_users = CustomUser.objects.filter(Q(email=data),is_manager=False )
# 			if associated_users.exists():
# 				for user in associated_users:
# 					subject = "Password Reset Requested"
# 					email_template_name = "password/password_reset_email.txt"
# 					c = {
# 					"email":user.email,
# 					'domain':'127.0.0.1:8000',
# 					'site_name': 'JengaCart',
# 					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
# 					'token': default_token_generator.make_token(user),
# 					'protocol': 'https',
# 					}
# 					email = render_to_string(email_template_name, c)
                    
# 					try:
# 						send_mail(subject, email, 'jenga@susrecomm.co.ke', [user.email], fail_silently=False)
# 					except BadHeaderError:

# 						return HttpResponse('Invalid header found.')
						
# 					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
# 					return redirect ("/password_reset/done/")
# 			messages.error(request, 'An invalid email has been entered.')
# 	password_reset_form = PasswordResetForm()
# 	return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})


def reset(request):
  error=''
  password_reset_form = PasswordResetForm()
  template = loader.get_template('password/password_reset.html')
  context = {
    'error': error,
    'password_reset_form': password_reset_form,
  }
  
  return HttpResponse(template.render(context, request))

def password_reset_request(request):
    if request.method == "POST":
        meta = CompanyMeta.objects.get(id=1)
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            u = CustomUser.objects.filter(Q(email=data))
            if u.exists():
                user = CustomUser.objects.get(email=data)
                if not user.is_manager:
                    subject = "Password Reset Request"
                    plaintext = loader.get_template('password/password_reset_email.txt')
                    htmltemp = loader.get_template('password/password_reset_email.html')
                    c = {
					"email":user.email,
                    "uname":user.first_name,
					'domain': meta.url,
					'site_name': meta.name,
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': meta.protocol,
					}
                    text_content = plaintext.render(c)
                    html_content = htmltemp.render(c)
                    try:
                        msg = EmailMultiAlternatives(subject, text_content, 'JengaCart <jenga@susrecomm.co.ke>', [user.email], headers = {'Reply-To': 'jenga@susrecomm.co.ke'})
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')

                    return redirect ("/password_reset/done/")
						

                else:
                    error=400
                    return redirect ("/pass_reset_e/"+str(error))

            else:
                error=401
                    
            return redirect ("/pass_reset_e/"+str(error))
            
def password_reset_mini(request):
    if request.method == "POST":
            meta = CompanyMeta.objects.get(id=1)
            data = request.POST['mail']
            
            user = CustomUser.objects.get(email=data)
                
            subject = "Password Reset Requested"
            plaintext = loader.get_template('password/password_reset_email.txt')
            htmltemp = loader.get_template('password/password_reset_email.html')
            c = {
					"email":user.email,
                    "uname":user.first_name,
					'domain': meta.url,
					'site_name': meta.name,
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': meta.protocol,
					}
            text_content = plaintext.render(c)
            html_content = htmltemp.render(c)
            try:
                        msg = EmailMultiAlternatives(subject, text_content, 'JengaCart <jenga@susrecomm.co.ke>', [user.email], headers = {'Reply-To': 'jenga@susrecomm.co.ke'})
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
            except BadHeaderError:
                        return HttpResponse('Invalid header found.')

            response = {
        'success':'Password Reset Initiated Successfully!' 
            }
    else:
         response = {
        'errors':'Invalid Request!' 
            }

    
    return JsonResponse(response)
        
       

 
						

               

def pass_e(request, id):
  if id == 401:
    error='Invalid Email Provided'
  elif id == 400:
      error='You Are Part Of The Management. Kindy Request The Administrator For A Password Reset '

  password_reset_form = PasswordResetForm()
  template = loader.get_template('password/password_reset.html')
  context = {
    'error': error,
    'password_reset_form': password_reset_form,
  }
  
  return HttpResponse(template.render(context, request))

	     
		

