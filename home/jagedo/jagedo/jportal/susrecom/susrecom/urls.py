"""susrecom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import include
from django.contrib.auth import views as auth_views
from accounts.views import  LoginFormView
from accounts.verify import  ActivateAccount
from accounts import reset, verify, views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', include('core.urls')),
    path('vendors/', include('vendors.urls')),
    path('accs/', include('accounts.urls')),
    path('custs/', include('customers.urls')),
    path('mans/', include('management.urls')),
    path('logistics/', include('logistics.urls')),
    path('fundis/', include('experts.urls')),
    path('api/v1/', include('mpesa.urls')),
    path('admin/', admin.site.urls),
    path('login/', LoginFormView.as_view(redirect_authenticated_user=True), name='login'),
    path('log-in/', views.login_auth, name='log-in'),
    path('logout/', views.logout_view, name='logout'),
    # path("tsms", views.sms, name="tsms"),
    path("v_change/<int:id>", verify.v_change, name="v_change"),
    path("v_phone/", verify.number_adjust, name="v_phone"),
    path("v_cresend/<int:id>", verify.code_resend, name="v_cresend"),
    path("v_account/", verify.verify_sms, name="v_account"),
    path("v_sms/<int:id>", verify.v_sms, name="v_sms"),
    path("account_verified/<int:id>", verify.verified, name="account_verified"),
    path("v_failed/<int:id>", verify.vfailed, name="v_failed"),
    path("v_resend/<int:id>", verify.vmail, name="v_resend"),
    path('e_verify/<int:id>', verify.e_verify, name='e_verify'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path("password_reset/", reset.reset, name="password_reset"),
    path("password_reset_sub/", reset.password_reset_request, name="password_reset_sub"),
    path("pass_reset_e/<int:id>", reset.pass_e, name="password_reset_sub"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'),  
    # path('sys/', include('django.contrib.auth.urls')), 
      
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.custom_page_not_found_view"
handler500 = "core.views.custom_server_error_view"


