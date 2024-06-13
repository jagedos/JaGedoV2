from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products
from core.models import OrderCarts, Orders, Reviews, Responses, WishList,jobs
from accounts.models import CustomUser,Profile , Tkeys, CompanyMeta
from vendors.models import Vproducts,Shops
from django.contrib import messages
from experts.models import Fields, Skills, Certs, Wdays, Pcategories, Milestones, Quotations, Quote_items, \
Quote_milestones
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
import json, random, africastalking, re
from django.forms.models import model_to_dict
from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
@customer_watch
def index(request):
  title='All_Job_Requests'
  acts = jobs.objects.filter(customer=request.user.id).order_by('-id')
  page = request.GET.get('page', 1)

  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('jobs.html')
  context = {
    'actives': actives,
    'title' : title
  }
  return HttpResponse(template.render(context, request))

@login_required
@customer_watch
def pending(request):
  title='Pending_Job_Requests'
  acts = jobs.objects.filter(status__lte=3,is_assigned=False,customer=request.user.id).order_by('-id')
  page = request.GET.get('page', 1)

  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('jobs.html')
  context = {
    'actives': actives,
    'title' : title
  }
  return HttpResponse(template.render(context, request))


@login_required
@customer_watch
def active(request):
  title='Active_Jobs'
  acts = jobs.objects.filter(status=4,customer=request.user.id).order_by('-id')
  page = request.GET.get('page', 1)

  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('jobs.html')
  context = {
    'actives': actives,
    'title' : title
  }
  return HttpResponse(template.render(context, request))


@login_required
@customer_watch
def iquotes(request,id):
  title='Quotations'
  acts = Quotations.objects.filter(job=id, is_selected=True,is_approved=False, is_rejected=False).order_by('-id')
  page = request.GET.get('page', 1)

  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('bids.html')
  context = {
    'actives': actives,
    'title' : title
  }
  return HttpResponse(template.render(context, request))



@login_required
@customer_watch
def pquotes(request):
  title='Pending_Quotations'
  user=request.user.pk
  acts = Quotations.objects.filter(job__customer=user, is_selected=True,is_approved=False, is_rejected=False).order_by('-id')
  page = request.GET.get('page', 1)

  paginator = Paginator(acts, 4)
  try:
        actives = paginator.page(page)
  except PageNotAnInteger:
        actives = paginator.page(1)
  except EmptyPage:
        actives = paginator.page(paginator.num_pages)
  template = loader.get_template('pbids.html')
  context = {
    'actives': actives,
    'title' : title
  }
  return HttpResponse(template.render(context, request))


@login_required
def quote_detail(request,serial):
  
  items = Quote_items.objects.filter(serial=serial)
  stat = Quote_milestones.objects.filter(serial=serial)
  order = Quotations.objects.get(serial=serial)
  wrk = jobs.objects.get(id=order.job.pk)
  meta = CompanyMeta.objects.get(id=1)
  template = loader.get_template('quote.html')
  context = {
    'items': items,
    'order': order,
    'meta': meta,
    'stat': stat,
    'gigs' : wrk,
    
  }
  return HttpResponse(template.render(context, request))


def confirm(request, id):
  member = Quotations.objects.filter(id=id)
  if member.exists():
        find=member.first()
        total=find.total
        fjob=find.job.pk
        ex=find.expert.pk
        expert=CustomUser.objects.get(id=ex)
        ms=Quote_milestones.objects.filter(quote=id)
        miles=ms.count()
        installments=round(total/miles)

        m=Quote_milestones.objects.filter(quote=id, milestone=1)
        mx=m.first()

        code= find.job.customer.first_name+str(mx.pk)
        my_datetime = datetime.now()
        member.update(is_selected=True,is_approved=True,is_active=True, updated_at=my_datetime)
        ms.update(fee=installments)
        m.update(pcode=code,is_active=True)
        Quotations.objects.filter(job=fjob).exclude(id=id).update(is_rejected=True)
        jobs.objects.filter(id=fjob).update(is_assigned=True,status=4,expert=expert)

        approvemail(id)
        
        encoded_serial = urlsafe_base64_encode(force_bytes(find.serial))

        messages.success(request, "Quote Approved successfully. ")
        response = {"success": "Quote Approved successfully.", "serial": encoded_serial}
  return JsonResponse(response)


def approvemail(id):
  meta = CompanyMeta.objects.get(id=1)

  checks = Quotations.objects.filter(id=id)
  if checks.exists():
    fnd=checks.first()
    chks = jobs.objects.get(id=fnd.job.pk)
    user = CustomUser.objects.get(id=chks.customer.pk)
    first = user.first_name
    email = user.email
    serial = chks.serial
    jid = chks.pk
    m=Quote_milestones.objects.filter(quote=id, is_active=True).first()
    pay=m.fee
    
    subject = "Quote_Approval_Confirmation"
  
    htmltemp = loader.get_template('alerts/qack_email.html')
    c = {
	  "email":email,
    "uname":first,
	  'domain': meta.url,
	  'site_name': meta.name,
	  'site_order': id,
    'job_order': jid,
    'serial': serial,
	  'protocol': meta.protocol,
    'pay': pay,
					}
    html_content = htmltemp.render(c)
    try:
      msg = EmailMultiAlternatives(subject, html_content, 'JaGedo <alerts@jagedo.co.ke>', [user.email], headers = {'Reply-To': 'alerts@jagedo.co.ke'})
      msg.attach_alternative(html_content, "text/html")
      msg.send()
    except BadHeaderError:
            return HttpResponse('Invalid header found.')

    approve_sms(id)
    msg='SUCCESS.'
    return msg
    
 
  else:

   msg='FAIL'
   return msg



def approve_sms(id):
  chks = Quotations.objects.filter(id=id).first()
  m=Quote_milestones.objects.filter(quote=id, is_active=True).first()
  pay=m.fee
  fee = format(pay, ",.2f")
  

  user = CustomUser.objects.get(id=chks.job.customer.pk)
  num = user.phone_number
  phone = re.sub(r'^.', '+254', num).split(",")
  name = user.first_name
  message =  "Dear "+name+",\n You Have approved the quote #0"+str(id)+".\n Kindly make the first installment of "+str(fee)+"  for work to begin ."
  items = Tkeys.objects.get()
  username =  items.u_name
  api_key =  items.u_key

  africastalking.initialize(username, api_key)

  sms = africastalking.SMS

  sms.send(message, phone)


@login_required
def miles_detail(request,uidb64):
  serial = force_str(urlsafe_base64_decode(uidb64))
  stat = Quote_milestones.objects.filter(serial=serial)
  ptitles='Project_Milestones'
  
  meta = CompanyMeta.objects.get(id=1)
  template = loader.get_template('project.html')
  context = {
    'meta': meta,
    'gigs' : stat,
    'ptitle': ptitles
    
  }
  return HttpResponse(template.render(context, request))

def pload(request, id):
  check =Quote_milestones.objects.filter(id=id).first()
  
  
  mymember = model_to_dict(check)

  response = mymember

  return JsonResponse(response, safe=False)