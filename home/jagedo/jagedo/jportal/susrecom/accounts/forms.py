from logging import PlaceHolder
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from accounts.models import  CustomUser
from vendors.models import Counties

class VsignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : John'}),required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : Doe'}),required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Example : johndoegmail.com','pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}),required=True)
    national_id = forms.CharField(required=True)    
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : 0722000111','autocomplete': 'off','minlength': 10, 'maxlength': 10,'pattern': '[0]{1}[0-9]{9}',
    'title' : "Phone_Number Must Be 10 Digit(s) & Must Begin With A Zero e.g. 0722000111"}),required=True)
    county = forms.ModelChoiceField(queryset=Counties.objects.all(), empty_label="Select Resident County", required=True)
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : Embakasi, Nairobi'}),required=True)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("first_name", "last_name","email","national_id","phone_number", "password1", "password2")
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_vendor = True
        user.save()
        return user


class CsignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : John'}),required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : Doe'}),required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Example : johndoegmail.com','pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}),required=True)
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : 0722000111','autocomplete': 'off','minlength': 10, 'maxlength': 10,'pattern': '[0]{1}[0-9]{9}',
    'data-bs-toggle' : "tooltip",'title' : "Phone_Number Must Be 10 Digit(s) & Must Begin With A Zero e.g. 0722000111"}),required=True)
    county = forms.ModelChoiceField(queryset=Counties.objects.all(), empty_label="Select Resident County", required=True)
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : Embakasi, Nairobi'}),required=True)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("first_name", "last_name","email","phone_number","county","location", "password1", "password2")
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_customer = True
        user.save()
        return user


class DsignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : John'}),required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : Doe'}),required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Example : johndoegmail.com','pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}),required=True)
    national_id = forms.CharField(required=True)    
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : 0722000111','autocomplete': 'off','minlength': 10, 'maxlength': 10,'pattern': '[0]{1}[0-9]{9}',
    'title' : "Phone_Number Must Be 10 Digit(s) & Must Begin With A Zero e.g. 0722000111"}),required=True)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("first_name", "last_name","email","national_id","phone_number", "password1", "password2")
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_delivery = True
        user.save()
        return user

class EsignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : John'}),required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : Doe'}),required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Example : johndoegmail.com','pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}),required=True)
    national_id = forms.CharField(required=True)    
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : 0722000111','autocomplete': 'off','minlength': 10, 'maxlength': 10,'pattern': '[0]{1}[0-9]{9}',
    'title' : "Phone_Number Must Be 10 Digit(s) & Must Begin With A Zero e.g. 0722000111"}),required=True)
    county = forms.ModelChoiceField(queryset=Counties.objects.all(), empty_label="Select Resident County", required=True)
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Example : Embakasi, Nairobi'}),required=True)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("first_name", "last_name","email","national_id","phone_number","location", "password1", "password2")
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_expert = True
        user.save()
        return user

