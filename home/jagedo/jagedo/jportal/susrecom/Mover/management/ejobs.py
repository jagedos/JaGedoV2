from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from experts.models import (
    Fields,
    Skills,
    Certs,
    Wdays,
    Pcategories,
    Milestones,
    Quotations,
    Quote_items,
    Quote_milestones,
    ExpertCats,
    ExpertSkills,
    PartnerSkills,
)
from core.models import jobs, AssignedExpert
from django.contrib import messages
from accounts.models import CustomUser, Profile, Tkeys, CompanyMeta
import json, random, africastalking, re
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json
from django.utils.crypto import get_random_string
from accounts.decorators import (
    authentication_not_required,
    customer_watch,
    manager_watch,
    vendor_watch,
)
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from django.db import transaction


@login_required
@manager_watch
def index(request):
    title = "Requests_Pending_Review"
    acts = jobs.objects.filter(status__lte=0).order_by("-id")
    cats = ExpertCats.objects.all().order_by("-id")
    comps = ExpertSkills.objects.all().order_by("-id")
    skils = Skills.objects.all()
    exps = CustomUser.objects.filter(is_expert=True)

    template = loader.get_template("experts/mjobs/jobs.html")
    context = {
        "gigs": acts,
        "ptitle": title,
        "cats": cats,
        "skills": skils,
        "experts": exps,
        "rskills": comps,
    }
    return HttpResponse(template.render(context, request))


@login_required
def iquotes(request, id):
    title = "Quotations"
    acts = Quotations.objects.filter(
        job=id, is_selected=False, is_rejected=False
    ).order_by("-id")

    template = loader.get_template("experts/mjobs/quotes.html")
    context = {"gigs": acts, "ptitle": title}
    return HttpResponse(template.render(context, request))


@login_required
def nquotes(request, id):
    title = "New Quotations"
    act = Quotations.objects.filter(
        job=id, is_selected=False, is_approved=False, is_rejected=False
    )
    up = act.update(is_viewed=True)
    acts = act.order_by("-id")
    template = loader.get_template("experts/mjobs/quotes.html")
    context = {"gigs": acts, "ptitle": title}
    return HttpResponse(template.render(context, request))


def approve(request, id):
    member = Quotations.objects.filter(id=id)
    if member.exists():
        find = member.first()
        fjob = find.job.pk

        member.update(is_selected=True)

        Quotations.objects.filter(job=fjob).exclude(id=id).update(
            is_active=False, is_rejected=True
        )

        print(selmail(fjob))
        print(qc_sms(fjob))

        messages.success(request, "Quote Selected successfully. ")
        response = {"success": "Quote Selected successfully. ", "serial": find.serial}
    return JsonResponse(response)


def edita(request, id):
    products = jobs.objects.get(id=id)

    n = products.product

    if n:
        name = products.product.name
    else:
        name = "N/A"

    if products.skill:
        skil = products.skill.pk
    else:
        skil = 0

    if products.expert:
        cont = products.expert.pk
    else:
        cont = 0

    if products.doc == "documents/none.png":
        img = "<i><b>No Files Uploaded!</b></i>"

    else:
        img = ' <table width="100%" class="table table-striped table-bordered dt-responsive compact nowrap"> \
  <thead> \
    <tr> \
     <th>Image</th> \
      <th>Action</th> \
        </tr> </thead>\
          <tbody> \
             '

        img += (
            '<tr> \
      <td><img src="/media/'
            + str(products.doc)
            + '" width="70" class="img-thumbnail"  loading="lazy"></td> \
               <td><a href="/media/'
            + str(products.doc)
            + '" class="btn btn-xs btn-info btn-sm">Download</a></td> </tr>'
        )

    res = {
        "id": id,
        "name": name,
        "quantity": products.quantity,
        "category": products.job.pk,
        "rskill": products.rexpert.pk,
        "status": products.status,
        "start": products.start,
        "end": products.end,
        "description": products.description,
        "expert": cont,
        "skill": skil,
        "doc": img,
    }

    parameters = {
        "x": res,
    }
    response = parameters

    return JsonResponse(response, safe=False)


@transaction.atomic
def upreview(request):
    if request.method == "POST":
        r = request.POST["category"]
        start = request.POST["start"]
        end = request.POST["end"]

        experts = request.POST.getlist("expert")
        skil = request.POST["skill"]
        bid = request.POST["bid"]
        description = request.POST["description"]
        id = request.POST["hidden_id"]
        job = ExpertCats.objects.get(id=r)

        if experts:
            for i in experts:
                if i != "":
                    expert = i
                    user = CustomUser.objects.get(id=expert)
                    # add to assigned experts
                    AssignedExpert.objects.create(job_id=id, expert=user)

        skills = Skills.objects.get(id=skil)

        member = jobs.objects.get(id=id)
        member.job = job
        member.quantity = 1
        member.description = description
        member.start = start
        member.end = end
        member.skill = skills
        member.status = bid
        if experts:
            member.has_requests = True
        member.save()

        if int(member.status) == 1:
            conmail(id)

        response = {
            "success": "Request Updated Successfully.",
        }
        return JsonResponse(response)
    else:
        response = {"errors": "Invalid Request!"}
        return JsonResponse(response)


def conmail(id):
    meta = CompanyMeta.objects.get(id=1)
    checks = jobs.objects.filter(id=id)

    if checks.exists():
        chks = jobs.objects.get(id=id)
        to_emails = []  # Create an empty list to hold email addresses
        if chks.has_requests:
            # users = PartnerSkills.objects.filter(partner=chks.expert).first()
            users = AssignedExpert.objects.filter(job=id)
            for u in users:
                email = u.expert.email
                to_emails.append(email)
        else:
            users = PartnerSkills.objects.filter(skill=chks.skill.pk)

            for u in users:
                email = u.partner.email
                to_emails.append(email)  # Append each email to the list

        serial = chks.serial
        subject = "Bid_Invitation"
        htmltemp = loader.get_template("experts/galerts/bidsinvite.html")
        c = {
            "domain": meta.url,
            "site_name": meta.name,
            "site_order": id,
            "serial": serial,
            "protocol": meta.protocol,
            "category": chks.job.name,
            "skill": chks.skill.name,
            "start": chks.start,
            "end": chks.end,
            "description": chks.description,
        }
        html_content = htmltemp.render(c)

        try:
            msg = EmailMultiAlternatives(
                subject,
                html_content,
                "JaGedo <alerts@jagedo.co.ke>",
                to_emails,
                headers={"Reply-To": "alertsa@jagedo.co.ke"},
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except BadHeaderError:
            return HttpResponse("Invalid header found.")

        msg = "SUCCESS."
        return msg

    else:
        msg = "FAIL"
        return msg


def selmail(id):
    meta = CompanyMeta.objects.get(id=1)

    checks = jobs.objects.filter(id=id)
    if checks.exists():
        chks = jobs.objects.filter(id=id).first()
        user = CustomUser.objects.get(id=chks.customer.pk)
        first = user.first_name
        email = user.email
        serial = chks.serial

        subject = "Quotation Generated"

        htmltemp = loader.get_template("experts/galerts/qgen.html")
        c = {
            "email": email,
            "uname": first,
            "domain": meta.url,
            "site_name": meta.name,
            "site_order": id,
            "serial": serial,
            "protocol": meta.protocol,
            "category": chks.job.name,
            "skill": chks.skill.name,
            "start": chks.start,
            "end": chks.end,
            "description": chks.description,
        }
        html_content = htmltemp.render(c)
        try:
            msg = EmailMultiAlternatives(
                subject,
                html_content,
                "JaGedo <alerts@jagedo.co.ke>",
                [user.email],
                headers={"Reply-To": "alerts@jagedo.co.ke"},
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except BadHeaderError:
            return HttpResponse("Invalid header found.")

        msg = "SUCCESS."
        return msg

    else:
        msg = "FAIL"
        return msg


def qc_sms(id):
    chks = jobs.objects.filter(id=id).first()

    user = CustomUser.objects.get(id=chks.customer.pk)
    num = user.phone_number
    phone = re.sub(r"^.", "+254", num).split(",")
    name = user.first_name
    message = (
        "Dear "
        + name
        + ",\n Quote for the job #0"
        + str(id)
        + ", has been generated.\n Log into your account to approve it ."
    )
    sender = "SUSRECOMM"
    print(phone)
    items = Tkeys.objects.get()
    username = items.u_name
    api_key = items.u_key

    africastalking.initialize(username, api_key)

    sms = africastalking.SMS

    sms.send(message, phone, sender)


@login_required
@manager_watch
def newquotes(request):
    title = "Quotation_Requests"
    acts = jobs.objects.filter(status=1).order_by("-id")

    template = loader.get_template("experts/mjobs/nreq.html")
    context = {
        "gigs": acts,
        "ptitle": title,
    }
    return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def open(request):
    title = "Quotation_Requests"
    acts = jobs.objects.filter(status=1).order_by("-id")

    template = loader.get_template("experts/mjobs/qreq.html")
    context = {
        "gigs": acts,
        "ptitle": title,
    }
    return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def active(request):
    title = "Active_Jobs"
    acts = jobs.objects.filter(status=4, is_assigned=True).order_by("-id")

    template = loader.get_template("experts/mjobs/areq.html")
    context = {
        "gigs": acts,
        "ptitle": title,
    }
    return HttpResponse(template.render(context, request))


@login_required
@manager_watch
def create_quote(request, id):
    title = "New_Quotation"
    acts = jobs.objects.get(id=id)
    cats = Pcategories.objects.all().order_by("-id")
    skils = Skills.objects.all()
    aexps = AssignedExpert.objects.filter(job=id)
    exps = ""
    if aexps.exists():
        assexps = aexps
    else:
        exps = CustomUser.objects.filter(is_expert=True)

    crts = Milestones.objects.all()
    img = ""
    for m in crts:
        img += '<option value="' + str(m.pk) + '">' + str(m.name) + "</option>"

    template = loader.get_template("experts/mjobs/createquote.html")
    context = {
        "gigs": acts,
        "ptitle": title,
        "cats": cats,
        "skills": skils,
        "experts": exps,
        "aexperts": assexps,
        "aexps": aexps,
        "mstones": img,
    }
    return HttpResponse(template.render(context, request))


def encrypt_id(id):
    final = urlsafe_base64_encode(force_bytes(id))
    return final


def storequote(request):
    if request.method == "POST":
        labour = request.POST["labour"]
        items = request.POST.getlist("item")
        quantity = request.POST.getlist("quantity")
        price = request.POST.getlist("price")
        ctotal = request.POST.getlist("ctotal")
        total = request.POST["total"]
        miles = request.POST.getlist("milestone")
        work = request.POST.getlist("work")
        expert = request.POST["expert"]

        mval = int(request.POST["mval"])
        mlen = len(miles)

        if not mlen == mval:
            response = {
                "errors": "Kindly Provide All The Milestones !",
            }
        else:
            jid = request.POST["hidden_id"]
            job = jobs.objects.get(id=jid)
            user = CustomUser.objects.get(id=expert)

            code = get_random_string(length=10)
            u_id = "Qjobs|" + code

            if job.has_expert:
                member = Quotations(
                    serial=u_id, job=job, labour=labour, total=total, expert=user
                )
                member.save()
            else:
                member = Quotations(
                    serial=u_id, job=job, labour=labour, total=total, expert=user
                )
                member.save()

            quote = Quotations.objects.get(id=member.pk)

            if items and quantity and price and ctotal:
                for i in range(len(items)):
                    item = items[i]
                    quant = quantity[i]
                    pri = price[i]
                    ctot = ctotal[i]
                    q_items = Quote_items(
                        serial=u_id,
                        quote=quote,
                        name=item,
                        quantity=quant,
                        price=pri,
                        total=ctot,
                        expert=user,
                    )
                    q_items.save()

            if miles and work:
                for m in range(len(miles)):
                    wrk = work[m]
                    ml = miles[m]
                    milst = Milestones.objects.get(id=ml)
                    peps = Quote_milestones(
                        serial=u_id, quote=quote, milestone=milst, work=wrk, expert=user
                    )
                    peps.save()

            serd = encrypt_id(u_id)

            response = {
                "success": "Quote Created Successfully.",
                "serial": serd,
            }

        return JsonResponse(response)
    else:
        response = {"errors": "Invalid Request!"}
        return JsonResponse(response)


@login_required
def quote_detail(request, uidb64):
    serial = force_str(urlsafe_base64_decode(uidb64))
    items = Quote_items.objects.filter(serial=serial)
    stat = Quote_milestones.objects.filter(serial=serial)
    order = Quotations.objects.get(serial=serial)
    wrk = jobs.objects.get(id=order.job.pk)
    meta = CompanyMeta.objects.get(id=1)
    template = loader.get_template("experts/mjobs/quote.html")
    context = {
        "items": items,
        "order": order,
        "meta": meta,
        "stat": stat,
        "gigs": wrk,
    }
    return HttpResponse(template.render(context, request))


def confirm(request, id):
    member = Quotations.objects.filter(id=id)
    if member.exists():
        find = member.first()
        total = find.total
        fjob = find.job.pk
        print(fjob)
        ex = find.expert.pk
        expert = CustomUser.objects.get(id=ex)
        ms = Quote_milestones.objects.filter(quote=id)
        miles = ms.count()
        installments = round(total / miles)

        m = Quote_milestones.objects.filter(quote=id, milestone=1)
        mx = m.first()

        code = find.job.customer.first_name + str(mx.pk)

        member.update(is_selected=True, is_active=True)
        ms.update(fee=installments)
        m.update(pcode=code, is_active=True)
        Quotations.objects.filter(job=fjob).exclude(id=id).update(is_rejected=True)
        jobs.objects.filter(id=fjob).update(is_assigned=True, status=4, expert=expert)

        messages.success(request, "Quote Approved successfully. ")
        response = {"success": "Quote Approved successfully.", "serial": find.serial}
    return JsonResponse(response)


@login_required
def miles_detail(request, uidb64):
    serial = force_str(urlsafe_base64_decode(uidb64))
    stat = Quote_milestones.objects.filter(serial=serial)
    ptitles = "Project_Milestones"

    meta = CompanyMeta.objects.get(id=1)
    template = loader.get_template("experts/mjobs/project.html")
    context = {"meta": meta, "gigs": stat, "ptitle": ptitles}
    return HttpResponse(template.render(context, request))


def delete(request, id):
    member = jobs.objects.get(id=id)
    member.delete()

    response = {"success": "Data Deleted successfully."}
    return JsonResponse(response)
