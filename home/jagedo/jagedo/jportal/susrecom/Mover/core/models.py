from enum import unique
from django.db import models
from items.models import Products
from management.models import Counties,PickUps
from vendors.models import Shops
from experts.models import Pitems, Pcategories, PartnerMeta, PartnerSkills, Skills,ExpertCats,ExpertSkills
from accounts.models import CustomUser
from vendors.models import Vproducts


# Create your models here.
class Carts(models.Model):
  vproduct = models.ForeignKey(Products, on_delete=models.SET_NULL, blank=True, null=True)
  quantity = models.IntegerField(default=0)
  customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  is_initiated = models.BooleanField(default=False)
  is_paid = models.BooleanField(default=False)
  admin = models.ForeignKey(CustomUser,related_name='admins',on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.vproduct.product.name

class TpayCarts(models.Model):
  pcode = models.CharField(default='None', max_length=255)
  amount = models.DecimalField(max_digits = 10,default=0,decimal_places = 2)
  paid   =   models.DecimalField(max_digits = 10,default=0,decimal_places = 2)
  customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  is_sent = models.BooleanField(default=False)
  is_paid = models.BooleanField(default=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.pcode



class OrderCarts(models.Model):
  vproduct = models.ForeignKey(Products, on_delete=models.SET_NULL, blank=True, null=True)
  serial = models.CharField(default='None',unique=False, max_length=255)
  quantity = models.IntegerField(default=0)
  price = models.DecimalField(max_digits = 10,decimal_places = 2)
  discount = models.DecimalField(default=0,max_digits = 10,decimal_places = 2)
  final_price = models.DecimalField(max_digits = 10,decimal_places = 2)
  customer = models.ForeignKey(CustomUser,related_name="customerc", on_delete=models.SET_NULL, blank=True, null=True)
  status = models.IntegerField(default=0)
  action_at = models.DateTimeField(null=True)
  is_initiated = models.BooleanField(default=False)
  is_reviewed = models.BooleanField(default=False)
  admin = models.ForeignKey(CustomUser,related_name='adminc',on_delete=models.SET_NULL, blank=True, null=True)
  is_assigned = models.BooleanField(default=False)
  shop = models.ForeignKey(Shops, on_delete=models.SET_NULL, blank=True, null=True)
  note = models.CharField(null=True,unique=False, max_length=255)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.vproduct

class Orders(models.Model):
  serial = models.CharField(default='None',unique=True, max_length=255)
  final_price = models.DecimalField(max_digits = 10,decimal_places = 2)
  status = models.IntegerField(default=0)
  has_paid = models.BooleanField(default=False)
  delivery_method = models.IntegerField(default=0)
  pickup = models.ForeignKey(PickUps,default=0, on_delete=models.SET_NULL, blank=True, null=True)
  county = models.ForeignKey(Counties, on_delete=models.SET_NULL, blank=True, null=True)
  directions = models.CharField(default='None',unique=False, max_length=255)
  customer = models.ForeignKey(CustomUser,related_name="customer", on_delete=models.SET_NULL, blank=True, null=True)
  is_initiated = models.BooleanField(default=False)
  admin = models.ForeignKey(CustomUser,related_name="admin",on_delete=models.SET_NULL, blank=True, null=True)
  is_assigned = models.BooleanField(default=False)
  shop = models.ForeignKey(Shops, on_delete=models.SET_NULL, blank=True, null=True)
  note = models.CharField(null=True,unique=False, max_length=255)
  action_at = models.DateTimeField(null=True)
  eta = models.DateTimeField(null=True)
  del_at = models.DateTimeField(null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.serial

  class Meta:
        verbose_name = "Orders"
        verbose_name_plural = "Customer_Orders"
        ordering = ['-created_at']

class Reviews(models.Model):
  vproduct = models.ForeignKey(Products, on_delete=models.SET_NULL, blank=True, null=True)
  serial = models.CharField(default='None',unique=False, max_length=255)
  rating = models.DecimalField(max_digits = 10,decimal_places = 2)
  review = models.TextField(default='None')
  customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  shop = models.ForeignKey(Shops, on_delete=models.SET_NULL, blank=True, null=True)
  is_disabled = models.BooleanField(default=False)
  is_viewed = models.BooleanField(default=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.vproduct

  class Meta:
        verbose_name = "Reviews"
        verbose_name_plural = "Product_Reviews"
        ordering = ['-created_at']

class Responses(models.Model):
  review = models.ForeignKey(Reviews, on_delete=models.SET_NULL, blank=True, null=True)
  response = models.TextField(default='None')
  respondent = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  is_disabled = models.BooleanField(default=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.review



class WishList(models.Model):
  vproduct = models.ForeignKey(Vproducts, on_delete=models.SET_NULL, blank=True, null=True)
  customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.vproduct

  class Meta:
        verbose_name = "WishList"
        verbose_name_plural = "Saved_Items"
        ordering = ['-created_at']

class  Tracker(models.Model):
  tid = models.CharField(default='None',unique=True, max_length=255)
  sid = models.CharField(default='None',unique=False, max_length=255)
  eta = models.DateTimeField(null=True)
  transport = models.IntegerField(default=0)
  note = models.CharField(null=True,unique=False, max_length=255)
  vendor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  shop = models.ForeignKey(Shops, on_delete=models.SET_NULL, blank=True, null=True)
  status = models.BooleanField(default=False)
  is_confirmed = models.BooleanField(default=False)
  action_at = models.DateTimeField(null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.tid

class PCarts(models.Model):
  job = models.ForeignKey(ExpertCats, on_delete=models.SET_NULL, blank=True, null=True)
  expert = models.ForeignKey(ExpertSkills, on_delete=models.SET_NULL, blank=True, null=True)
  product = models.ForeignKey(Pitems, on_delete=models.SET_NULL, blank=True, null=True)
  quantity = models.IntegerField(default=0)
  customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  description = models.TextField(default='None',unique=False)
  start = models.DateField(null=True)
  end = models.DateField(null=True)
  doc = models.ImageField(default='documents/none.png', upload_to='documents/')
  is_direct = models.BooleanField(default=False)
  is_initiated = models.BooleanField(default=False)
  admin = models.ForeignKey(CustomUser,related_name='padmins',on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.job



class jobs(models.Model):
    serial = models.CharField(default="None", unique=False, max_length=255)
    job = models.ForeignKey(
        ExpertCats, on_delete=models.SET_NULL, blank=True, null=True
    )
    rexpert = models.ForeignKey(
        ExpertSkills, on_delete=models.SET_NULL, blank=True, null=True
    )
    product = models.ForeignKey(
        Pitems, on_delete=models.SET_NULL, blank=True, null=True
    )
    quantity = models.IntegerField(default=0)
    customer = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, blank=True, null=True
    )
    description = models.TextField(default="None", unique=False)
    start = models.DateField(null=True)
    end = models.DateField(null=True)
    doc = models.ImageField(default="documents/none.png", upload_to="documents/")
    delivery_method = models.IntegerField(default=0)
    pickup = models.ForeignKey(
        PickUps, on_delete=models.SET_NULL, blank=True, null=True
    )
    location = models.ForeignKey(
        Counties, on_delete=models.SET_NULL, blank=True, null=True
    )
    directions = models.CharField(default="None", unique=False, max_length=255)
    is_direct = models.BooleanField(default=False)
    is_initiated = models.BooleanField(default=False)
    is_assigned = models.BooleanField(default=False)
    admin = models.ForeignKey(
        CustomUser,
        related_name="jadmins",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    status = models.IntegerField(default=0)
    skill = models.ForeignKey(Skills, on_delete=models.SET_NULL, blank=True, null=True)
    has_expert = models.BooleanField(default=False)
    has_requests = models.BooleanField(default=False)
    expert = models.ForeignKey(
        CustomUser,
        related_name="fundi",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job


# assigned expert
class AssignedExpert(models.Model):
    job = models.ForeignKey(jobs, on_delete=models.SET_NULL, blank=True, null=True)
    expert = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, blank=True, null=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job

