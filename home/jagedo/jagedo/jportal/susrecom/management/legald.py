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
import json
from django.db.models import Q, F, Count, Sum, Avg
from math import ceil
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.utils.crypto import get_random_string
from accounts.decorators import authentication_not_required, customer_watch, manager_watch, vendor_watch
from django.contrib.auth.decorators import login_required
from management.models import LegalDocuments, LegalDocumentTypes

# Create your views here.
# datatable view for legal documents types  
class LegalDocumentTypesDataTableView(BaseDatatableView):
    columns = ['name', 'global_status','status']
    search_fields = ['name__icontains']

    def render_column(self, row, column):
        if column == 'global_status':
            if row.is_global:
                return f"<span class='badge badge-success'>Global</span>"
            
            elif row.is_customer:
                return f"<span class='badge badge-primary'>Customer</span>"
            elif row.is_partner:
                return f"<span class='badge badge-warning'>Partner</span>"
            elif row.is_vendor:
                return f"<span class='badge badge-info'>Vendor</span>"
            else:
                return ''
        else:
            return super().render_column(row, column)

    def get_initial_queryset(self):
        queryset = LegalDocumentTypes.objects.all()
        return queryset

    def filter_queryset(self, qs):
        search = self.request.POST.get(u'search[value]', None)
        if search:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{field: search})
            qs = qs.filter(query)
        return qs
    

# datatable view for legal documents
class LegalDocumentsDataTableView(BaseDatatableView):
    columns = ['type','status','user']
    search_fields = ['type__name__icontains']

    def get_initial_queryset(self):
        queryset = LegalDocuments.objects.all()
        return queryset

    def filter_queryset(self, qs):
        search = self.request.POST.get(u'search[value]', None)
        if search:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{field: search})
            qs = qs.filter(query)
        return qs
    

# function to get legal documents types
def get_legal_document_types(request):
    types = LegalDocumentTypes.objects.all()
    template = loader.get_template('legal/types.html')
    context = {
    'types': types,
    }
    return HttpResponse(template.render(context, request))

# function to get legal documents
def get_legal_documents(request):
    types = LegalDocumentTypes.objects.all()
    template = loader.get_template('legal/documents.html')
    context = {
    'types': types,
    }
    return HttpResponse(template.render(context, request))

# fuctiion to add legal document type
def add_legal_document_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        iglobal = request.POST.get('global')
        user = request.user.id

        

       
        if name and iglobal:
            if iglobal == 'All':
               is_global = True
               is_customer = False
               is_vendor = False
               is_partner = False
            elif iglobal == 'Customer':
               is_global = False
               is_customer = True
               is_vendor = False
               is_partner = False
            elif iglobal == 'Vendor':
               is_global = False
               is_customer = False
               is_vendor = True
               is_partner = False
            elif iglobal == 'Partner':
               is_global = False
               is_customer = False
               is_vendor = False
               is_partner = True

            try:
                type = LegalDocumentTypes.objects.get(name=name)
                if type:
                    return JsonResponse({'errors': 'Legal document type already exists'})
            except:
                type = LegalDocumentTypes.objects.create(name=name, is_global=is_global, is_customer=is_customer, is_partner=is_partner, is_vendor=is_vendor, user_id=user)
                if type:
                    return JsonResponse({'success': 'Legal document type added successfully'})
                else:
                    return JsonResponse({'errors': 'Failed to add legal document type'})
        else:
            return JsonResponse({'errors': 'Please fill all the fields'})
    else:
        return JsonResponse({'errors': 'Invalid request'})
    

# function to update legal document type
def update_legal_document_type(request):
    if request.method == 'POST':
        id = request.POST.get('hidden_id')
        name = request.POST.get('name')
        iglobal = request.POST.get('global')
        user = request.user.id
       
        if name and iglobal and id:
            if iglobal == 'All':
               is_global = True
               is_customer = False
               is_vendor = False
               is_partner = False
            elif iglobal == 'Customer':
               is_global = False
               is_customer = True
               is_vendor = False
               is_partner = False
            elif iglobal == 'Vendor':
               is_global = False
               is_customer = False
               is_vendor = True
               is_partner = False
            elif iglobal == 'Partner':
               is_global = False
               is_customer = False
               is_vendor = False
               is_partner = True

            try:
                type = LegalDocumentTypes.objects.get(id=id)
                if type:
                    type.name = name
                    type.is_global = is_global
                    type.is_customer = is_customer
                    type.is_vendor = is_vendor
                    type.is_partner = is_partner
                    type.user_id = user
                    type.save()
                    return JsonResponse({'success': 'Legal document type updated successfully'})
                else:
                    return JsonResponse({'errors': 'Legal document type not found'})
            except:
                return JsonResponse({'errors': 'Failed to update legal document type'})
        else:
            return JsonResponse({'errors': 'Please fill all the fields'})
    else:
        return JsonResponse({'errors': 'Invalid request'})
    


# get legal document type by id
def editatype(request, id):
  type = LegalDocumentTypes.objects.get(id=id)

  parameters = { 'id': type.pk,
                 'name': type.name,
                 'is_global': type.is_global,
                 'is_customer': type.is_customer,
                 'is_vendor': type.is_vendor,
                 'is_partner': type.is_partner,
                 

   }
  response = parameters

  return JsonResponse(response, safe=False)

# function to delete legal document type
def delete_legal_document_type(request,id):
  type = LegalDocumentTypes.objects.get(id=id)
  # delete attached documents
  documents = LegalDocuments.objects.filter(type=type).delete()
  # delete type
  type.delete()

  response = {
        'success':'Data Deleted successfully.' 
            }
  return JsonResponse(response)


# function to add and upload legal document
def add_legal_document(request):
    if request.method == 'POST':
        type = request.POST.get('type')
        status = request.POST.get('status')
        user = request.user.id
        # allow only pdf files
        if request.FILES['document'].content_type != 'application/pdf':
            return JsonResponse({'errors': 'Please upload pdf file'})
        
        document = request.FILES.get('document')
        if type and status and document:
            try:
                type = LegalDocumentTypes.objects.get(id=type)
                if type:
                    try:
                        document = LegalDocuments.objects.get(type=type)
                        if document:
                            return JsonResponse({'errors': 'Document already exists'})
                    except:
                        document = LegalDocuments.objects.create(type=type, status=status, document=document, user_id=user)
                        if document:
                            return JsonResponse({'success': 'Document added successfully'})
                        else:
                            return JsonResponse({'errors': 'Failed to add document'})
                else:
                    return JsonResponse({'errors': 'Legal document type not found'})
            except:
                return JsonResponse({'errors': 'Failed to add document'})
        else:
            return JsonResponse({'errors': 'Please fill all the fields'})
    else:
        return JsonResponse({'errors': 'Invalid request'})
    

# function to update legal document
def update_legal_document(request):
    if request.method == 'POST':
        id = request.POST.get('hidden_id')
        type = request.POST.get('type')
        status = request.POST.get('status')
        user = request.user.id
        # allow only pdf files if document is uploaded
        if request.FILES.get('document'):
            if request.FILES['document'].content_type != 'application/pdf':
                return JsonResponse({'errors': 'Please upload pdf file'})
        
        doc = request.FILES.get('document')
        if type and status and id:
            try:
                type = LegalDocumentTypes.objects.get(id=type)
                if type:
                    try:
                        document = LegalDocuments.objects.get(id=id)
                        if document:
                            document.type = type
                            document.status = status
                            document.user_id = user
                            if doc:
                                document.document = doc
                            document.save()
                            return JsonResponse({'success': 'Document updated successfully'})
                        else:
                            return JsonResponse({'errors': 'Document not found'})
                    except:
                        return JsonResponse({'errors': 'Failed to update document'})
                else:
                    return JsonResponse({'errors': 'Legal document type not found'})
            except:
                return JsonResponse({'errors': 'Failed to update document'})
        else:
            return JsonResponse({'errors': 'Please fill all the fields'})
    else:
        return JsonResponse({'errors': 'Invalid request'})
    

# get legal document by id
def editadocument(request, id):
  document = LegalDocuments.objects.get(id=id)

  parameters = { 'id': document.pk,
                 'type': document.type_id,
                 'name': document.type.name,
                 'status': document.status,
                 'document': str(document.document),
                 

   }
  response = parameters

  return JsonResponse(response, safe=False)

# function to delete legal document
def delete_legal_document(request,id):
    document = LegalDocuments.objects.get(id=id)
    # delete document
    document.delete()
    
    response = {
            'success':'Data Deleted successfully.' 
                }
    return JsonResponse(response)





    




