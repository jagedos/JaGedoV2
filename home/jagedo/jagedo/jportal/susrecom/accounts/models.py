from django.db import models
from email.policy import default
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from management.models import Counties, UserTypes

# Create your models here.
class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=False, null=True,default=None)
    email = models.EmailField(unique=True, db_index=True)
    national_id = models.CharField(default="None",max_length=255, blank=True)
    phone_number = models.CharField(max_length=255, unique=True,db_index=True)
    location = models.CharField(max_length=255, unique=False ,null=True)
    usertype = models.ForeignKey(
        UserTypes, default=2, on_delete=models.SET_NULL, blank=True, null=True
    )
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_delivery = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self): 
      return f"{self.first_name} {self.last_name} | {self.phone_number}"
    
  

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    v_type = models.CharField(default=0,max_length=255, blank=True)
    v_key = models.CharField(default=0,max_length=255, blank=True)
    county = models.ForeignKey(Counties, related_name="countyp", default=29,on_delete=models.SET_NULL, blank=True, null=True)
    location = models.ForeignKey(Counties, default=48,on_delete=models.SET_NULL, blank=True, null=True)
    has_details = models.BooleanField(default=False)
    is_reviewer = models.BooleanField(default=False)
 

@receiver(post_save, sender=CustomUser)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()

class Tkeys(models.Model):
    u_name = models.CharField(max_length=255, blank=True)
    u_key = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Tkeys"
        verbose_name_plural = "SMS_Keys"

class CompanyMeta(models.Model):
  name = models.CharField(max_length=255)
  url = models.CharField(max_length=255)
  address = models.CharField(default='Nairobi',max_length=255)
  email = models.CharField(default='None',max_length=255)
  protocol = models.CharField(max_length=255)
  phone = models.CharField(max_length=255)
  about = models.TextField(default='None',unique=False)
  dd_vendor = models.IntegerField(default=0)
  dd_office = models.IntegerField(default=0)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "CompanyMeta"
        verbose_name_plural = "Company_Meta_Data"


class Vdocs(models.Model):
  idfront = models.ImageField(default='documents/none.png', upload_to='documents/')
  idback = models.ImageField(default='documents/none.png', upload_to='documents/')
  bizreg = models.ImageField(default='documents/none.png', upload_to='documents/')
  taxcomp = models.ImageField(default='documents/none.png', upload_to='documents/')
  vendor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Vdocs"
        verbose_name_plural = "Vendor_Documents"