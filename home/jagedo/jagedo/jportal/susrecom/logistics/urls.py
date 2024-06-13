from django.urls import path
from logistics import views

urlpatterns = [
    path('', views.index, name='index'),
   
   
   
]