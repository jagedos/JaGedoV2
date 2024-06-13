from django.urls import path
from accounts import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vsign/', views.index, name='vsign'),
    path('vstore/', views.register, name='vstore'),
    path('csign/', views.cindex, name='csign'),
    path('cstore/', views.cregister, name='cstore'),
    path('dsign/', views.dindex, name='dsign'),
    path('logistics_store/', views.dregister, name='logistics_store'),
    path('esign/', views.eindex, name='esign'),
    path('cosign/', views.coindex, name='cosign'),
    path('estore/', views.eregister, name='estore'),
    path('lswitch/', views.logswitch, name='lswitch'),
   
]