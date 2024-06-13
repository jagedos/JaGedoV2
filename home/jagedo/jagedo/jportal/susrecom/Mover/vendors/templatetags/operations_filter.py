from django import template
from django.db.models import Sum, Count
from vendors.models import Vproducts, Shops
from items.models import Pimages, Products, Categories
from experts.models import Peimages, Pitems
from core.models import (
    Carts,
    OrderCarts,
    Orders,
    Reviews,
    Responses,
    WishList,
    Tracker,
    PCarts,
    jobs,
    AssignedExpert,
)
from experts.models import (
    Quotations,
    Quote_items,
    Quote_milestones,
    PartnerSkills,
    PartnerMeta,
    ContractorMeta,
    ContractorCategory,
)
from django.db.models import Avg
from accounts.models import CompanyMeta, CustomUser
from datetime import datetime, timedelta, time, date
from django.utils.html import escape
from management.models import Actions, Permissions
import os

register = template.Library()


@register.filter
def price_final(id):
    req = Products.objects.get(id=id)
    final = req.price - (req.price * (0))
    return final


@register.filter
def price_fin(id):
    req = Vproducts.objects.get(id=id)
    final = req.price - (req.price * (0))
    return final


@register.filter
def cover_image(id):
    pi = Pimages.objects.filter(product=id)
    if pi.exists():
        pic = pi.first()
        final = (
            '<img src="/media/'
            + str(pic.cover)
            + '" class="img-thumbnail" width="100" loading="lazy">'
        )
    else:
        final = "No_Image"

    return final


@register.filter
def pcover_image(id):
    pi = Peimages.objects.filter(product=id)
    if pi.exists():
        pic = pi.first()
        final = (
            '<img src="/media/'
            + str(pic.cover)
            + '" class="img-thumbnail" width="100" loading="lazy">'
        )
    else:
        final = "No_Image"

    return final


@register.filter
def docs_viewer(id):
    file_path = f"/media/{str(id)}"
    file_extension = os.path.splitext(file_path)[1].lower()
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    if file_extension in image_extensions:
        final = (
            f'<img src="{file_path}" class="img-thumbnail" width="100" loading="lazy">'
        )
        return final
    else:
        return "Document"


@register.filter
def docs_checker(id):
    file_path = f"/media/{str(id)}"
    file_extension = os.path.splitext(file_path)[1].lower()
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    if file_extension in image_extensions:
        final = True

    else:
        final = False

    return final


@register.filter
def agreement_id(id):
    final = int(id) + 5

    return final


@register.filter
def reg_as(id):
    id = int(id)
    find = PartnerMeta.objects.filter(partner=id)
    if find.exists():
        reg = find.first().regas
        if reg == 1:
            final = "<b>Professional</b>"
        elif reg == 2:
            final = "<b>Fundi</b>"
        elif reg == 3:
            final = "<b>Contractor</b>"
    else:
        final = "<b>Not_Registered</b>"

    return final


@register.filter
def reg_ast(id):
    id = int(id)
    find = PartnerMeta.objects.filter(partner=id)
    if find.exists():
        reg = find.first().regas
        if reg == 3:
            final = 3
        else:
            final = 0
    else:
        final = 0

    return final


@register.filter
def reg_skills(id):
    id = int(id)
    findx = PartnerMeta.objects.filter(partner=id).first()
    if findx and findx.regas == 3:
        find = ContractorCategory.objects.filter(partner=id)
        if find.exists():
            skills = "<ul>"
            for f in find:
                skills += (
                    "<li><b>("
                    + str(f.field.name)
                    + ") -"
                    + str(f.nca.name)
                    + "</b></li>"
                )
            skills += "</ul>"

            final = skills
        else:
            final = "<ul><li><b>No_Category_Registered</b></li></ul>"
    else:
        find = PartnerSkills.objects.filter(partner=id)
        if find.exists():
            skills = "<ul>"
            for f in find:
                # Ensure that the relationships exist
                skill_name = escape(
                    getattr(getattr(f, "skill", None), "name", "Unknown")
                )
                field_name = escape(
                    getattr(
                        getattr(getattr(f, "skill", None), "field", None),
                        "name",
                        "Unknown",
                    )
                )

                skills += f"<li><b>({field_name}) - {skill_name}</b></li>"
            skills += "</ul>"

            final = skills
        else:
            final = "<ul><li><b>No_Skill_Registered</b></li></ul>"

    return final


@register.filter
def reg_details(id):
    id = int(id)
    find = PartnerMeta.objects.filter(partner=id)
    if find.exists():
        reg = find.first()
        if reg.regas == 3:
            contractor = ContractorMeta.objects.filter(partner=id).first()
            if contractor:
                final = (
                    "<b>Company_Name : </b>"
                    + contractor.company_name
                    + "</br> <b>Company_Email : </b> "
                    + contractor.company_email
                    + "</br> \
                        <b>Company_Phone : </b>"
                    + contractor.company_phone
                )
            else:
                final = "<b>Company Details Not Registered</b>"
        else:
            final = (
                "<b>Email : </b>"
                + reg.partner.email
                + "</br> <b>Phone : </b> "
                + reg.partner.phone_number
                + "</br> \
                      <b>National_Id : </b>"
                + reg.partner.national_id
                + "</br> <b>Location :</b> "
                + reg.partner.profile.county.name
                + ", "
            )

    else:
        reg = CustomUser.objects.get(id=id)
        final = (
            "<b>Email : </b>"
            + reg.email
            + "</br> <b>Phone : </b> "
            + reg.phone_number
            + "</br> \
                      <b>National_Id : </b>"
            + reg.national_id
            + "</br> <b>Location :</b> "
            + reg.profile.county.name
            + ", "
        )

    return final


@register.filter
def cov_image(id):
    pi = Pimages.objects.filter(product=id)
    if pi.exists():
        pic = pi.first()
        final = (
            '<img src="/media/'
            + str(pic.cover)
            + '" alt="'
            + str(pic.product.name)
            + '" title="'
            + str(pic.product.name)
            + '" loading="lazy">'
        )
    else:
        final = "No_Image"
    return final


@register.filter
def shop_cover_image(id):
    if not id:
        return "No_Image"

    try:
        id = int(id)
    except ValueError:
        return "No_Image"

    pi = Pimages.objects.filter(product=id)
    if pi.exists():
        pic = pi.first()
        final = (
            '<img class="product-img" src="/media/'
            + str(pic.cover)
            + '" alt="'
            + str(pic.product.name)
            + '" title="'
            + str(pic.product.name)
            + '" loading="lazy">'
        )
    else:
        final = "No_Image"

    return final


@register.filter
def slider_image(id):
    pi = Pimages.objects.filter(product=id)
    if pi.exists():
        pic = pi.first()
        final = (
            '<img class="w-100" src="/media/'
            + str(pic.cover)
            + '" alt="'
            + str(pic.product.name)
            + '" title="'
            + str(pic.product.name)
            + '" loading="lazy">'
        )
    else:
        final = "No_Image"

    return final


@register.filter
def gig_cover_image(id):
    pic = Peimages.objects.filter(product=id).first()
    final = (
        '<img class="product-img" src="/media/'
        + str(pic.cover)
        + '" alt="'
        + str(pic.product.name)
        + '" title="'
        + str(pic.product.name)
        + '" loading="lazy">'
    )
    return final


@register.filter
def cart_price(id):
    cart = Carts.objects.get(id=id)
    req = Products.objects.get(id=cart.vproduct.id)
    price = req.price - (req.price * (0))
    final = price * cart.quantity
    return final


@register.filter
def cart_image(id):
    pic = Pimages.objects.filter(product=id).first()
    final = '<img src="/media/' + str(pic.cover) + '" loading="lazy">'
    return final


@register.filter
def cart_totals(id):
    carts = Carts.objects.filter(customer=id)
    finl = 0
    for c in carts:
        req = Products.objects.get(id=c.vproduct.id)
        price = req.price - (0)
        fin = price * c.quantity
        finl += fin
    final = str(finl)
    return final


@register.filter
def product_check(id):
    req = Vproducts.objects.get(id=id)
    item = req.product.id
    price = round(req.price - (req.price * (req.discount / 100)), 2)
    check = Vproducts.objects.filter(product__id=item, price__lt=price, status=True)
    if check.exists():
        final = 0
    else:
        final = 1
    return final


@register.filter
def pcat_total(id):
    num = Pitems.objects.filter(category=id, status=True).count()
    final = num
    return final


@register.filter
def cat_total(id):
    num = Products.objects.filter(category=id, status=True).count()
    final = num
    return final


@register.filter
def scat_total(id, shop):
    num = Vproducts.objects.filter(
        product__category=id, shop__id=shop, status=True
    ).count()
    final = num
    return final


@register.filter
def shop_total(id):
    num = Vproducts.objects.filter(shop=id, status=True).count()
    final = num
    return final


@register.filter
def rev_total(id):
    num = Reviews.objects.filter(vproduct=id, is_disabled=False).count()
    final = num
    return final


@register.filter
def srev_total(id):
    num = Reviews.objects.filter(vproduct__shop=id, is_disabled=False).count()
    final = num
    return final


@register.filter
def avg_total(id):
    num = Reviews.objects.filter(vproduct=id, is_disabled=False).aggregate(
        Avg("rating")
    )
    if num["rating__avg"] == None:
        final = 0
    else:
        final = num["rating__avg"]

    return final


@register.filter
def savg_total(id):
    num = Reviews.objects.filter(vproduct__shop=id, is_disabled=False).aggregate(
        Avg("rating")
    )
    if num["rating__avg"] == None:
        final = 0
    else:
        final = num["rating__avg"]

    return final


@register.filter
def pending_reviews(id):
    checks = Orders.objects.filter(customer=id, status=2)
    serials = checks.values_list("serial", flat=True)
    finder = OrderCarts.objects.filter(serial__in=serials, is_reviewed=False).count()
    final = finder
    return final


@register.filter
def wishlist(id):
    finder = WishList.objects.filter(customer=id).count()
    final = finder
    return final


@register.filter
def rev_rating(id):
    order = OrderCarts.objects.get(id=id)
    req = Reviews.objects.filter(vproduct=order.vproduct, serial=order.serial)
    if req.exists():
        finder = req.first()
        final = finder.rating
    else:
        final = 0

    return final


@register.filter
def get_review(id):
    order = OrderCarts.objects.get(id=id)
    req = Reviews.objects.filter(vproduct=order.vproduct, serial=order.serial)
    if req.exists():
        finder = req.first()
        final = (
            '<textarea name="review" class="form-control" rows="6" placeholder="" disabled>'
            + finder.review
            + "</textarea>"
        )
    else:
        final = "<center><h2><i>NO REVIEW</i></h2></center>"

    return final


@register.filter
def rev_id(id):
    order = OrderCarts.objects.get(id=id)
    req = Reviews.objects.filter(vproduct=order.vproduct, serial=order.serial)
    if req.exists():
        finder = req.first()
        final = finder.id
    else:
        final = 0

    return final


@register.filter
def vrev_total(id):
    num = Reviews.objects.filter(shop__vendor=id, is_viewed=False).count()
    final = num
    return final


@register.filter
def assign_delays(id):
    meta = CompanyMeta.objects.get(id=1)

    total = (
        Orders.objects.filter(is_assigned=0, status=0)
        .values("serial", "shop", "status")
        .count()
    )
    final = total
    return final


@register.filter
def vendor_delays(id):
    meta = CompanyMeta.objects.get(id=1)

    time_threshold = datetime.now() - timedelta(hours=meta.dd_vendor)
    total = (
        OrderCarts.objects.filter(created_at__lt=time_threshold, status=0)
        .values("serial", "shop", "status")
        .annotate(dcount=Count("shop"))
        .count()
    )
    final = total
    return final


@register.filter
def order_delays(id):
    meta = CompanyMeta.objects.get(id=1)

    time_threshold = datetime.now() - timedelta(hours=meta.dd_office)
    total = (
        OrderCarts.objects.filter(status=0)
        .values("serial", "shop", "status")
        .annotate(dcount=Count("shop"))
        .count()
    )

    final = total
    return final


@register.filter
def in_transit(id):
    time_threshold = datetime.now()
    total = Tracker.objects.filter(status=False).count()
    final = total
    return final


@register.filter
def delivery_delays(id):
    time_threshold = datetime.now()

    total = Tracker.objects.filter(eta__lt=time_threshold, status=False).count()

    final = total
    return final


@register.filter
def unverified_dels(id):
    total = Tracker.objects.filter(sid=id, status=True).count()

    final = total
    return final


@register.simple_tag
def cartq(id, client):
    find = Carts.objects.filter(vproduct=id, customer=client)
    if find.exists():
        data = find.first()
        count = data.quantity

    else:
        count = 1

    final = count
    return final


@register.simple_tag
def cartpq(id, client):
    find = PCarts.objects.filter(product=id, customer=client)
    if find.exists():
        data = find.first()
        count = data.quantity

    else:
        count = 1

    final = count
    return final


@register.simple_tag
def job_check(id, user):
    exp = user
    expcheck = jobs.objects.filter(id=id, has_requests=True)
    bids = Quotations.objects.filter(job=id, expert=exp)
    if bids.exists():
        fin = 0
    elif expcheck.exists():
        det = expcheck.first()
        if det.expert != None:
            oexp = det.expert.pk
        else:
            oexp = 0
        finder = AssignedExpert.objects.filter(job=id, expert=exp)
        if finder.exists():
            fundi = finder.first().expert.pk
        if fundi == exp or fundi == oexp:
            fin = 1
        else:
            fin = 0
    else:
        fin = 1

    final = fin
    return final


@register.filter
def find_serial(id):
    total = Quotations.objects.filter(
        job=id, is_selected=True, is_approved=True, is_rejected=False, is_active=True
    )
    if total.exists():
        find = total.first()
        serial = find.serial
    else:
        serial = "None"
    final = serial
    return final


@register.filter
def pjobs(id):
    total = jobs.objects.filter(status__lte=3, is_assigned=False, customer=id).count()
    final = total
    return final


@register.filter
def pqs(id):
    total = Quotations.objects.filter(
        job__customer=id, is_selected=True, is_approved=False, is_rejected=False
    ).count()
    final = total
    return final


@register.filter
def actjobs(id):
    total = jobs.objects.filter(status=4, is_assigned=True, customer=id).count()
    final = total
    return final


@register.filter
def quotecheck(id):
    total = Quotations.objects.filter(
        job=id, is_approved=False, is_rejected=False, is_viewed=False
    )
    if total.exists():
        fin = 1
    else:
        fin = 0
    final = fin
    return final


@register.filter
def fmiles(id):
    total = Quote_milestones.objects.filter(
        quote=id, is_active=True, is_completed=False
    ).first()
    if total:
        fin = total.milestone.name
    else:
        fin = "None"

    final = fin
    return final


@register.filter
def fimiles(id):
    total = Quote_milestones.objects.filter(
        quote=id, is_active=True, is_completed=False
    ).first()
    if total:
        fin = total.pk
    else:
        fin = "None"

    final = fin
    return final


@register.filter
def find_sk(id):
    total = PartnerSkills.objects.filter(skill=id)
    if total.exists():
        find = 1
    else:
        find = 0

    final = int(find)
    return final


# filter for getting first category name
@register.filter
def first_category_name(id):
    total = Categories.objects.all().first()
    final = total.name
    return final


@register.filter
def has_permission(user, action_name):
    try:
        action = Actions.objects.get(name=action_name)
        return Permissions.objects.filter(
            user_type=user.usertype, action=action, status=True
        ).exists()
    except Actions.DoesNotExist:
        return False
