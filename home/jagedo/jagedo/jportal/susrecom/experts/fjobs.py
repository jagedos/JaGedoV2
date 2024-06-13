from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from core.models import OrderCarts,Orders,jobs,Pcategories
from items.models import Categories, Products
from django.forms.models import model_to_dict
from vendors.models import Counties
from django.utils.crypto import get_random_string
from experts.models import Fields, Skills, Certs, Wdays, Pcategories, Milestones, Quotations, Quote_items, \
Quote_milestones
from accounts.models import CustomUser, Vdocs, Profile, CompanyMeta, Tkeys
from experts.models import Fields, Skills, Certs,Wdays, PartnerCerts, PartnerMeta, PartnerSkills, PartnerTimes
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json, random, africastalking, re
from django.db.models import Sum, Count, Q
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.decorators import authentication_not_required, customer_watch, manager_watch,logistics_watch, experts_watch
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
@experts_watch
def create_quote(request,id):
  title='New_Quotation'
  acts = jobs.objects.get(id=id)
  cats = Pcategories.objects.all().order_by('-id')
  skils = Skills.objects.all()
  

  crts= Milestones.objects.all()
  img=''
  for m in crts:
    img+='<option value="'+str(m.pk)+'">'+ str(m.name) +'</option>'

  
  template = loader.get_template('work/createquote.html')
  context = {
    'gigs': acts,
    'ptitle' : title,
    'cats' : cats,
    'skills' : skils,
    'mstones' : img
  }
  return HttpResponse(template.render(context, request))

def encrypt_id(id):
    final = urlsafe_base64_encode(force_bytes(id))
    return final

def storequote(request):
  if request.method =='POST':
     labour = request.POST['labour']
     items = request.POST.getlist('item')
     quantity = request.POST.getlist('quantity')
     price = request.POST.getlist('price')
     ctotal = request.POST.getlist('ctotal')
     total= request.POST['total']
     miles = request.POST.getlist('milestone')
     work = request.POST.getlist('work')
     expert= request.POST['expert']

     jid=request.POST['hidden_id']
     bids=Quotations.objects.filter(job=jid,expert=expert)

     mval= int(request.POST['mval'])
     mlen= len(miles)

     if not mlen == mval:
         response = {
          'errors':'Kindly Provide All The Milestones !' ,
            }
     elif bids.exists():
          response = {
          'errors':'Quotation Already Created  !' ,
            }
     else:
       job= jobs.objects.get(id=jid)
       user = CustomUser.objects.get(id=expert)

       code = get_random_string(length=10)
       u_id = 'Qjobs|'+code
     
       if job.has_expert:
          member = Quotations(serial=u_id,job=job,labour=labour, total=total, expert=user)
          member.save()
       else:
            member = Quotations(serial=u_id,job=job,labour=labour, total=total, expert=user)
            member.save()

       quote = Quotations.objects.get(id=member.pk)

       if items and quantity and price and ctotal:
         for i in range(len(items)):
          item = items[i]
          quant = quantity[i]
          pri = price[i]
          ctot = ctotal[i]
          q_items= Quote_items(serial=u_id,quote=quote, name=item, quantity=quant,price=pri, total=ctot,expert=user)
          q_items.save()
          
       if miles and work:
         for m in range(len(miles)):
          wrk= work[m]
          ml=miles[m]
          milst = Milestones.objects.get(id=ml)
          peps = Quote_milestones(serial=u_id,quote=quote, milestone=milst, work=wrk, expert=user)
          peps.save()

       serd=encrypt_id(u_id)
     
       response = {
          'success':'Quote Created Successfully.' ,
          'serial' : serd,
            }

     return JsonResponse(response)
  else:
    response = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(response)



@login_required
def quote_detail(request,uidb64):
  serial = force_str(urlsafe_base64_decode(uidb64))
  items = Quote_items.objects.filter(serial=serial)
  stat = Quote_milestones.objects.filter(serial=serial)
  order = Quotations.objects.get(serial=serial)
  wrk = jobs.objects.get(id=order.job.pk)
  meta = CompanyMeta.objects.get(id=1)
  template = loader.get_template('work/quote.html')
  context = {
    'items': items,
    'order': order,
    'meta': meta,
    'stat': stat,
    'gigs' : wrk,
    
  }
  return HttpResponse(template.render(context, request))


@login_required
@experts_watch
def gigs(request):
  title='Available_Jobs'
  cats = Pcategories.objects.all().order_by('-id')
  skils = PartnerSkills.objects.filter(partner=request.user.id).values_list('skill', flat=True)
  exps = CustomUser.objects.filter(is_expert=True)

  acts = jobs.objects.filter(skill__in=skils,status__lte=3).order_by('-id')
  
  template = loader.get_template('work/jobs.html')
  context = {
    'gigs': acts,
    'ptitle' : title,
    'cats' : cats,
    'skills' : skils,
    'experts' : exps
  }
  return HttpResponse(template.render(context, request))



def bids(request):
  title='Pending_Bids'
  acts = Quotations.objects.filter(expert=request.user.id, is_selected=False, is_rejected=False).order_by('-id')
  
  
  template = loader.get_template('work/bids.html')
  context = {
    'gigs': acts,
    'ptitle' : title,
  }
  return HttpResponse(template.render(context, request))


def abids(request):
  title='Approved_Bids'
  acts = Quotations.objects.filter(expert=request.user.id, is_selected=True,is_approved=True, is_rejected=False).order_by('-id')
  
  
  template = loader.get_template('work/bids.html')
  context = {
    'gigs': acts,
    'ptitle' : title,
  }
  return HttpResponse(template.render(context, request))


def rbids(request):
  title='Rejected_Bids'
  acts = Quotations.objects.filter(expert=request.user.id, is_selected=False, is_rejected=True).order_by('-id')
  
  
  template = loader.get_template('work/bids.html')
  context = {
    'gigs': acts,
    'ptitle' : title,
  }
  return HttpResponse(template.render(context, request))



@login_required
def active(request):
  title='Active_Jobs'
  acts = jobs.objects.filter(status=4,is_assigned=True).order_by('-id')
 


  
  template = loader.get_template('work/areq.html')
  context = {
    'gigs': acts,
    'ptitle' : title,
  }
  return HttpResponse(template.render(context, request))


def closemiles(request, id):
  miles=Quote_milestones.objects.filter(id=id)
  x=miles.first()
  quote=x.quote.pk
  expert=x.expert
  job=x.quote.job.pk
  
  miles.update(is_active=False, is_completed=True)
  checker=Quote_milestones.objects.filter(quote=quote, expert=expert).exclude(id=id)
  if checker.exists():
    nw=checker.earliest('pk')
    new=nw.pk
    Quote_milestones.objects.filter(id=new).update(is_active=True)
  else:
    Quotations.objects.filter(id=quote).update(is_active=False,is_completed=True)
    jobs.objects.filter(id=job).update(status=5)

  compmail(id)
  response = {
        'success':'Milestone Closed successfully\.' 
            }
  return JsonResponse(response)


def compmail(id):
  meta = CompanyMeta.objects.get(id=1)

  checks = Quote_milestones.objects.filter(id=id)
  if checks.exists():
    x=checks.first()
    quote=x.quote.pk
    expert=x.expert
    job=x.quote.job.pk
    omile=x.milestone.name
    customer=x.quote.job.customer.pk
    user = CustomUser.objects.get(id=customer)
    first = user.first_name
    email = user.email
    serial = x.quote.job.serial
    find = Quote_milestones.objects.filter(quote=quote, is_active=True)
    

    if find.exists():
       subject = "Milestone_Completion_Confirmation"
       fn=find.first()
       cmile=fn.milestone.name
       pay=fn.fee
       htmltemp = loader.get_template('work/alerts/miles.html')
       c = {
	         "email":email,
           "uname":first,
	         'domain': meta.url,
	         'site_name': meta.name,
	         'site_order': quote,
           'job_order': job,
           'serial': serial,
	         'protocol': meta.protocol,
           'omiles': omile,
           'cmiles': cmile,
           'pay': pay,

					}
       
    else:
        subject = "Job_Completion_Confirmation"
        htmltemp = loader.get_template('work/alerts/complete.html')
        c = {
	         "email":email,
           "uname":first,
	         'domain': meta.url,
	         'site_name': meta.name,
	         'site_order': quote,
           'job_order': job,
           'serial': serial,
	         'protocol': meta.protocol,
           'omiles': omile,
					}
  
    
    html_content = htmltemp.render(c)
    try:
      msg = EmailMultiAlternatives(subject, html_content, 'JaGedo <alerts@jagedo.co.ke>', [user.email], headers = {'Reply-To': 'alerts@jagedo.co.ke'})
      msg.attach_alternative(html_content, "text/html")
      msg.send()
    except BadHeaderError:
            return HttpResponse('Invalid header found.')
    
    comp_sms(id)
    msg='SUCCESS.'
    return msg
    
 
  else:

   msg='FAIL'
   return msg



def comp_sms(id):
  chks = Quote_milestones.objects.filter(id=id).first()
  omiles=chks.milestone.name
  job=chks.quote.job.pk
  m=Quote_milestones.objects.filter(quote=chks.quote.pk, is_active=True)
  if m.exists():
    mf=m.first()
    cmiles=mf.milestone.name
    pay=mf.fee
    fee = format(pay, ",.2f")
  

  user = CustomUser.objects.get(id=chks.quote.job.customer.pk)
  num = user.phone_number
  phone = re.sub(r'^.', '+254', num).split(",")
  name = user.first_name
  if m.exists():
    message =  "Dear "+name+",\n "+str(omiles)+" for job #"+str(job)+" has been completed. "+str(cmiles)+" has been activated.\n Kindly make the installment of "+str(fee)+"  for work to begin ."
  else:
    message =  "Dear "+name+",\n "+str(omiles)+" for job #"+str(job)+" has been completed. This marks the end of the project.\n Thanks for choosing JaGedo ."

  items = Tkeys.objects.get()
  username =  items.u_name
  api_key =  items.u_key

  africastalking.initialize(username, api_key)

  sms = africastalking.SMS

  print(sms.send(message, phone))


