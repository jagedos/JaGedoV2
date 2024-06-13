from django import template
from django.db.models import Sum
from vendors.models import Vproducts, Shops
from items.models import Pimages, Products,Categories
from core.models import Carts, OrderCarts, Orders, Reviews, Responses, WishList,jobs
from django.db.models import Avg
from experts.models import Fields, Skills, Certs,Wdays, PartnerCerts, PartnerMeta, PartnerSkills, PartnerTimes, Quotations
from accounts.models import CompanyMeta,CustomUser
from datetime import datetime, timedelta, time, date
register = template.Library()


@register.filter
def mtoday_sales(id):
    
    total= OrderCarts.objects.filter(created_at__date=date.today()).exclude(status=3).aggregate(sum=Sum('final_price'))
    if  total['sum'] == None:
        count=0
     
    else:
        count= total['sum']
    
    final = count
    return final 


@register.filter
def total_vendors(id):
    total = CustomUser.objects.filter(is_vendor=True,is_active=True).count()
    final = total
    return final 



@register.filter
def total_customers(id):
    total = CustomUser.objects.filter(is_customer=True,is_active=True).count()
    final = total
    return final 

@register.filter
def total_managers(id):
    total = CustomUser.objects.filter(is_manager=True,is_active=True).count()
    final = total
    return final 

@register.filter
def total_partners(id):
    total = CustomUser.objects.filter(is_expert=True,is_active=True).count()
    final = total
    return final 

@register.filter
def deactivated(id):
    total = CustomUser.objects.filter(is_active=False).count()
    final = total
    return final 

@register.filter
def total_vpartners(id):
    total = CustomUser.objects.filter(
        is_expert=True, is_approved=True, is_active=True
    ).count()
    final = total
    return final


@register.filter
def total_uvpartners(id):
    total = CustomUser.objects.filter(
        is_expert=True, is_approved=False, is_active=True
    ).count()
    final = total
    return final


@register.filter
def totalusers(id):
    total = CustomUser.objects.all().count()
    final = total
    return final 


@register.filter
def tavailable(id):
    skils = PartnerSkills.objects.filter(partner=id).values_list('skill', flat=True)
    acts = jobs.objects.filter(skill__in=skils, status__lte=3).order_by('-id')
    fin = 0

    for a in acts:
        expcheck = jobs.objects.filter(id=a.pk, has_expert=True)
        bids = Quotations.objects.filter(job=a.pk, expert=id)

        if bids.exists():
            fin += 0  # This line is redundant but kept for consistency
        elif expcheck.exists():
            det = expcheck.first()
            if det and det.expert:
                fundi = det.expert.pk
                if fundi == id:
                    fin += 1
                else:
                    fin += 0  # This line is redundant but kept for consistency
            else:
                fin += 1  # Increment if no expert is found in the expcheck
        else:
            fin += 1  # Increment if no job with an expert is found

    total = fin
    final = total
    return final


@register.filter
def tpbids(id):
    total = Quotations.objects.filter(expert=id, is_rejected=True, is_approved=False).count()
    final = total
    return final 


@register.filter
def tabids(id):
    total = Quotations.objects.filter(expert=id, is_selected=True, is_approved=True,updated_at__date=date.today()).count()
    final = total
    return final 


@register.filter
def trbids(id):
    total = Quotations.objects.filter(expert=id, is_selected=True, is_rejected=True,created_at__date=date.today()).count()
    final = total
    return final 


@register.filter
def unverified_quotes(id):
    total = Quotations.objects.filter( is_selected=False,  is_approved=False, is_rejected=False, is_viewed=False).count()
    final = total
    return final 


@register.filter
def split_after_second(value, sep):
    parts = value.split(sep, 2)
    if len(parts) > 2:
        return f"{parts[0]},<br>{parts[1]},<br>{parts[2]}"
    else:
        return ''
