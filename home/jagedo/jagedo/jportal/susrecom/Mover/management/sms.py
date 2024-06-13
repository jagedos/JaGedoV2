from django_datatables_view.base_datatable_view import BaseDatatableView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from items.models import Categories, Products, Brands, Munits, Pimages
from vendors.models import Shops, Vproducts
from django.forms.models import model_to_dict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
import json, random, africastalking, re
from django.db.models import Q, F, Count, Sum, Avg
from math import ceil
from accounts.models import CompanyMeta, CustomUser, Tkeys
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.utils.crypto import get_random_string
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required
from management.models import SMS

# Create your views here.
# add, update, delete, list sms
class SMSListJson(BaseDatatableView):
    columns = ['id', 'message', 'status', 'receipient ','user', 'created_at', 'status']
    search_fields = [ 'message__icontains', 'receipient__icontains', 'user__icontains']

    def render_column(self, row, column):
        if column == 'status':
            if row.to_all:
                return f"<span class='badge badge-success'>All_System_Members</span>"
            
            elif row.to_customer:
                return f"<span class='badge badge-primary'>Customers</span>"
            elif row.to_partner:
                return f"<span class='badge badge-warning'>Partners</span>"
            elif row.to_vendor:
                return f"<span class='badge badge-info'>Vendor</span>"
            elif row.to_manager:
                return f"<span class='badge badge-success'>Managers</span>"
            else:
                return f"<span class='badge bg-gray'>Individual_Member</span>"
        else:
            return super().render_column(row, column)

    def get_initial_queryset(self):
        queryset = SMS.objects.all().order_by('-created_at')
        return queryset

    def filter_queryset(self, qs):
        search = self.request.POST.get(u'search[value]', None)
        if search:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{field: search})
            qs = qs.filter(query)
        return qs
    

# index function
@login_required
def index(request):
    # get active loans
    members=CustomUser.objects.filter(is_customer=True)
    template = loader.get_template('sms/sms.html')
    context = {
        'members': members,
    }
    return HttpResponse(template.render(context, request))

# send sms
@login_required
def send_sms(request):
    if request.method == 'POST':
        type = request.POST['r_type']
        if type != '2':
            if type == '1':
               users = CustomUser.objects.all()
            elif type == '3':
                users = CustomUser.objects.filter(is_customer=True)
            elif type == '4':
                users = CustomUser.objects.filter(is_vendor=True)
            elif type == '5':
                users = CustomUser.objects.filter(is_expert=True)
            elif type == '6':
                users = CustomUser.objects.filter(is_manager=True)

            nums = {re.sub(r'^.', '+254', ph) for user in users for ph in user.phone_number.split(",")}

            phone = list(nums)  # Convert the set back to a list if you need it in list format':

        else:
          receipient = request.POST['members']
          user = CustomUser.objects.get(id=receipient)
          num = user.phone_number
          phone = re.sub(r'^.', '+254', num).split(",")
          name = user.first_name

        message = request.POST['sms']
        items = Tkeys.objects.get()
        username =  items.u_name
        api_key =  items.u_key
        sender= "SUSRECOMM"


        africastalking.initialize(username, api_key)

        sms = africastalking.SMS

        sms.send(message, phone, sender)

        # save sms
        sms = SMS()
        sms.message = message
        sms.user_id = request.user.id
        if type == '1':
           sms.to_all = True 
        elif type == '3':
            sms.to_customer = True
        elif type == '4':
            sms.to_vendor = True
        elif type == '5':
            sms.to_partner = True
        elif type == '6':
            sms.to_manager = True
        else:
           sms.receipient_id = receipient
           sms.to_all = False
        sms.save()

        return JsonResponse({'success': 'SMS sent successfully'})
    

# delete sms
@login_required
def delete(request, id):
    sms = SMS.objects.get(id=id)
    sms.delete()
    return JsonResponse({'success': True, 'message': 'SMS deleted successfully'})

# search system users
def getall(request):
    
    search = request.GET.get('q', None)
    if search:
     dat = CustomUser.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(phone_number__icontains=search), is_active=True).values('id','first_name','last_name','phone_number')
     data = list(dat)
     response=data
     return JsonResponse(response, safe=False)
    else:
        return JsonResponse(data={'success': False,
                                          'errors': 'No mathing items found'})
