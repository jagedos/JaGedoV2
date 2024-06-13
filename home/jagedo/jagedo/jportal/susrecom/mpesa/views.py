from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth
import json, re
from core.models import Carts, OrderCarts, Orders, PCarts, Pcategories,jobs,TpayCarts
from experts.models import Quote_milestones
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
from mpesa.models import MpesaPayment


def getAccessToken(request):
    consumer_key = 'HjucYEGnoxcbdfuAW12DI4BRw5zf06dl'
    consumer_secret = 'pBwGumRRpPxI7DbY'
    api_URL = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']

    return HttpResponse(validated_mpesa_access_token)


def lipa_na_mpesa_online(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": 254719757227,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": 254719757227,  # replace with your phone number to get stk push
        "CallBackURL": "https://jagedo.co.ke/api/v1/c2b/callback",
        "AccountReference": "JaGedo",
        "TransactionDesc": "Testing stk push"
    }

    response = requests.post(api_url, json=request, headers=headers)
    return HttpResponse('success')


def lipa_cart(request):
   if request.method =='POST':
     cnum = request.POST['mphone'] 
     pcart= request.POST['phidden_id'] 
     phone = str(cnum).replace('0', '254', 1)
     dets=TpayCarts.objects.get(id=pcart)
     amount=int(dets.amount)
     ref=dets.pcode

     access_token = MpesaAccessToken.validated_mpesa_access_token
     api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
     headers = {"Authorization": "Bearer %s" % access_token}
     request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": phone,  # replace with your phone number to get stk push
        "CallBackURL": "https://jagedo.co.ke/api/v1/c2b/callback",
        "AccountReference": ref,
        "TransactionDesc": "JaGedo_STK_Push"
     }

     response = requests.post(api_url, json=request, headers=headers)
     respon = {
        'success':'Payment Submitted Successfully. Kindly Complete Transaction On Your Phone !' 
            }
     return JsonResponse(respon)

   else:
    respon = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(respon)


def lipa_ecart(request):
   if request.method =='POST':
     cnum = request.POST['mphone'] 
     pcart= request.POST['phidden_id'] 
     phone = str(cnum).replace('0', '254', 1)
     dets=Quote_milestones.objects.get(id=pcart)
     amount=int(dets.fee)
     ref=dets.pcode

     access_token = MpesaAccessToken.validated_mpesa_access_token
     api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
     headers = {"Authorization": "Bearer %s" % access_token}
     request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": phone,  # replace with your phone number to get stk push
        "CallBackURL": "https://jagedo.co.ke/api/v1/c2b/callback",
        "AccountReference": ref,
        "TransactionDesc": "JaGedo_STK_Push"
     }

     response = requests.post(api_url, json=request, headers=headers)
     respon = {
        'success':'Payment Submitted Successfully. Kindly Complete Transaction On Your Phone !' 
            }
     return JsonResponse(respon)

   else:
    respon = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(respon)



def lipa_conf(request):
   if request.method =='POST':
     
     pcart= request.POST['phidden_id'] 
    
     dets=TpayCarts.objects.filter(id=pcart,is_paid=True)
     if dets.exists():
         find=dets.first()
         cust=find.customer
         Carts.objects.filter(customer=cust).update(is_paid=True)


         respon = {
          'success':'Payment Confirmed Successfully !' 
            }
     else:
          respon = {
          'errors':'Payment Not Yet Received !' 
            }

     return JsonResponse(respon)

   else:
    respon = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(respon)


def lipa_econf(request):
   if request.method =='POST':
     
     pcart= request.POST['phidden_id'] 
    
     dets=Quote_milestones.objects.filter(id=pcart,is_paid=True)
    
     if dets.exists():
         find=dets.first()
        
         respon = {
          'success':'Payment Confirmed Successfully !' 
            }
     else:
          respon = {
          'errors':'Payment Not Yet Received !' 
            }

     return JsonResponse(respon)

   else:
    respon = {
        'errors':'Invalid Request!' 
            }
    return JsonResponse(respon)



@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://api.safaricom.co.ke/mpesa/c2b/v2/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://jagedo.co.ke/api/v1/c2b/confirmation",
               "ValidationURL": "https://jagedo.co.ke/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)

    return HttpResponse(response.text)


@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)

    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name='x',
        middle_name='x',
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],

    )
    payment.save()

    ref=payment.reference
    finder=TpayCarts.objects.filter(pcode=ref)
    if finder.exists():
        finder.update(paid=payment.amount,is_sent=True,is_paid=True)

    finder=Quote_milestones.objects.filter(pcode=ref)
    if finder.exists():
        finder.update(is_paid=True)



    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }

    return JsonResponse(dict(context))

