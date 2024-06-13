from tabnanny import verbose
from django.core.files.base import File
from django.db import models
import datetime
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

# Create your models here.
class Categories(models.Model):
  name = models.CharField(max_length=255)
  expert = models.BooleanField(default=False)
  slide = models.BooleanField(default=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Categories"
        verbose_name_plural = "Product_Categories"


  def __str__(self):
      return self.name
  


class Brands(models.Model):
  name = models.CharField(max_length=255)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Brands"
        verbose_name_plural = "Product_Brands"

  def __str__(self):
      return self.name

class Munits(models.Model):
  name = models.CharField(max_length=255)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Munits"
        verbose_name_plural = "Product_Measurement_Units"

  def __str__(self):
      return self.name

# class Products(models.Model):
#   name = models.CharField(max_length=255)
#   category = models.IntegerField()
#   brand = models.IntegerField(default=0)
#   stock = models.IntegerField(default=0)
#   price = models.DecimalField(max_digits = 10,decimal_places = 2)
#   updated_at = models.DateTimeField(auto_now=True)
#   created_at = models.DateTimeField(auto_now_add=True)

class Products(models.Model):
  name = models.CharField(max_length=255)
  category = models.ForeignKey(Categories, on_delete=models.SET_NULL, blank=True, null=True)
  brand = models.ForeignKey(Brands, on_delete=models.SET_NULL, blank=True, null=True)
  units = models.ForeignKey(Munits, on_delete=models.SET_NULL, blank=True, null=True)
  serial = models.CharField(default='None', max_length=255)
  description = models.TextField(default='None',unique=False)
  weight = models.DecimalField(default=0,max_digits = 10,decimal_places = 4)
  status = models.BooleanField(default=True)
  slide = models.BooleanField(default=False)
  price = models.DecimalField(max_digits = 10, default=0,decimal_places = 2)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Products"
        verbose_name_plural = "Products"

  def __str__(self):
      return self.name

class Pimages(models.Model):
  product = models.ForeignKey(Products, on_delete=models.SET_NULL, blank=True, null=True)
  cover = models.ImageField(default='products/none.png', upload_to='products/')
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Pimages"
        verbose_name_plural = "Product_Images"
  
  def save(self, *args, **kwargs):
    # Open the uploaded image
    im = Image.open(self.cover)

    # Resize the image
    im = im.resize((500, 500))

    # Save the resized image to a BytesIO object
    output = BytesIO()
    im.save(output, format='PNG', quality=100)
    output.seek(0)

    # Create a Django File object from the BytesIO object
    file = File(output, name=self.cover.name)

    # Save the File object to the cover field
    self.cover = file

    # Call the superclass save method
    super(Pimages, self).save(*args, **kwargs)
    

  def __str__(self):
      return self.product

