import functools
from django.shortcuts import redirect
from django.contrib import messages

def authentication_not_required(view_func, redirect_url="accounts:profile"):
    """
        this decorator ensures that a user is not logged in,
        if a user is logged in, the user will get redirected to 
        the url whose view name was passed to the redirect_url parameter
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request,*args, **kwargs)
        messages.error(request, "You need to be logged out")
        print("You need to be logged out")
        return redirect(redirect_url)
    return wrapper


def customer_watch(view_func, redirect_url="/accs/lswitch/"):
    """
        this decorator ensures that a user is customer,
       
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_customer:
            return view_func(request,*args, **kwargs)
        messages.error(request, "You Are Not Authorised To Access The Requested Resource")
        return redirect(redirect_url)
    return wrapper

def vendor_watch(view_func, redirect_url="/accs/lswitch/"):
    """
        this decorator ensures that a user is vendor,
       
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_vendor:
            return view_func(request,*args, **kwargs)
        messages.error(request, "You Are Not Authorised To Access The Requested Resource")
        return redirect(redirect_url)
    return wrapper


def manager_watch(view_func, redirect_url="/accs/lswitch/"):
    """
        this decorator ensures that a user is manager,
       
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_manager:
            return view_func(request,*args, **kwargs)
        messages.error(request, "You Are Not Authorised To Access The Requested Resource")
        return redirect(redirect_url)
    return wrapper



def logistics_watch(view_func, redirect_url="/accs/lswitch/"):
    """
        this decorator ensures that a user is logistics partner,
       
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_delivery:
            return view_func(request,*args, **kwargs)
        messages.error(request, "You Are Not Authorised To Access The Requested Resource")
        return redirect(redirect_url)
    return wrapper


def experts_watch(view_func, redirect_url="/accs/lswitch/"):
    """
        this decorator ensures that a user is logistics partner,
       
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_expert:
            return view_func(request,*args, **kwargs)
        messages.error(request, "You Are Not Authorised To Access The Requested Resource")
        return redirect(redirect_url)
    return wrapper