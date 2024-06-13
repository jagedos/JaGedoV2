from django.urls import path
from customers import views, jobs
from core.order import job_detail
from mpesa.views import lipa_cart, lipa_ecart, lipa_econf

urlpatterns = [ 
    path('', views.index, name='index'),
    path('active_orders/', views.active_orders, name='active_orders'),
    path('closed_orders/', views.closed_orders, name='closed_orders'),
    path('customer_profile/', views.profile, name='customer_profile'),
    path('pending_reviews/', views.reviews, name='pending_reviews'),
    path('call_reviews/', views.allreviews, name='call_reviews'),
    path('reviewdetails/<int:id>', views.edita, name='reviewdetails'),
    path('reviewdets/<int:id>', views.editr, name='reviewdets'),
    path('update_customer_details/', views.updaterecord, name='update_customer_details'),
    path('my_wishlist/', views.wishlist, name='my_wishlist'),
    path('del_wish/<int:id>', views.delwish, name='del_wish'),
    path('call_jobs/', jobs.index, name='call_jobs'),
    path('cjob_summary/<uidb64>', job_detail, name='cjob_summary'),
    path('pend_jobs/', jobs.pending, name='pend_jobs'),
    path('cactive_jobs/', jobs.active, name='cactive_jobs'),
    path('cqlists/<int:id>', jobs.iquotes, name='cqlists'),
    path('pend_quotes/', jobs.pquotes, name='pend_quotes'),
    path('cust_pquote/<str:serial>', jobs.quote_detail, name='cust_pquote'),
    path('acceptquote/<int:id>', jobs.confirm, name='acceptquote'),
    path('miles_summary/<uidb64>', jobs.miles_detail, name='miles_summary'),
    path('epayloader/<int:id>', jobs.pload, name='epayloader'),
    path('epushpay', lipa_ecart, name='epushpay'),
    path('epushconf', lipa_econf, name='epushconf'),
   
]