from django.db import models
from django.core.files.base import File
from accounts.models import CustomUser
from vendors.models import Counties
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

# Create your models here.
class Fields(models.Model):
  name = models.CharField(max_length=255)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Fields"
        verbose_name_plural = "Expert_Fields"



class Skills(models.Model):
  name = models.CharField(max_length=255)
  field = models.ForeignKey(Fields, on_delete=models.SET_NULL, blank=True, null=True)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Skills"
        verbose_name_plural = "Technical_Skills"


class Certs(models.Model):
  name = models.CharField(max_length=255)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Certs"
        verbose_name_plural = "Required_Certificate_List"


class Wdays(models.Model):
  name = models.CharField(max_length=255)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Wdays"
        verbose_name_plural = "Work_Days"
        ordering = ('id',)


class NcaFields(models.Model):
  name = models.CharField(max_length=255)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Fields"
        verbose_name_plural = "Expert_Fields"

class ContractorMeta(models.Model):
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(max_length=255)
    company_phone = models.CharField(max_length=255)
    company_cert = models.ImageField(default='documents/none.png', upload_to='documents/')
    pin_cert = models.ImageField(default='documents/none.png', upload_to='documents/')
    business_permit = models.ImageField(default='documents/none.png', upload_to='documents/')
    company_profile = models.ImageField(default='documents/none.png', upload_to='documents/')
    partner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ContractorCategory(models.Model):
     field = models.ForeignKey(Fields, on_delete=models.SET_NULL, blank=True, null=True)
     nca = models.ForeignKey(NcaFields, on_delete=models.SET_NULL, blank=True, null=True)
     partner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
     updated_at = models.DateTimeField(auto_now=True)
     created_at = models.DateTimeField(auto_now_add=True)

class ContractorPortfolio(models.Model):
      title = models.CharField(max_length=255, default='None', blank=True, null=True)
      category = models.ForeignKey(ContractorCategory, on_delete=models.SET_NULL, blank=True, null=True)
      profile = models.ImageField(default='documents/none.png', upload_to='documents/')
      updated_at = models.DateTimeField(auto_now=True)
      created_at = models.DateTimeField(auto_now_add=True)


class PartnerMeta(models.Model):
  location = models.ForeignKey(Counties, on_delete=models.SET_NULL, blank=True, null=True)
  gender = models.IntegerField(default=0)
  regas = models.IntegerField(default=0)
  yrs = models.IntegerField(default=0)
  field = models.ForeignKey(Fields, on_delete=models.SET_NULL, blank=True, null=True)
  availability = models.IntegerField(default=0)
  cv = models.ImageField(default='documents/none.png', upload_to='documents/')
  idfront = models.ImageField(default='documents/none.png', upload_to='documents/')
  idback = models.ImageField(default='documents/none.png', upload_to='documents/')
  approval_doc = models.ImageField(default='documents/none.png', upload_to='documents/')
  partner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "PartnerMeta"
        verbose_name_plural = "Partner_Details"


class PartnerSkills(models.Model):
  field = models.ForeignKey(Fields, on_delete=models.SET_NULL, blank=True, null=True)
  skill = models.ForeignKey(Skills, on_delete=models.SET_NULL, blank=True, null=True)
  partner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "PartnerSkills"
        verbose_name_plural = "Partner_Skills"


class PartnerCerts(models.Model):
  cert = models.ForeignKey(Certs, on_delete=models.SET_NULL, blank=True, null=True)
  doc = models.ImageField(default='documents/none.png', upload_to='documents/')
  partner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "PartnerCerts"
        verbose_name_plural = "Partner_Certificates"



class PartnerTimes(models.Model):
  day = models.ForeignKey(Wdays, on_delete=models.SET_NULL, blank=True, null=True)
  start = models.TimeField()
  end = models.TimeField()
  partner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "PartnerTimes"
        verbose_name_plural = "Partner_Availability"



class Pcategories(models.Model):
  name = models.CharField(max_length=255)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Pcategories"
        verbose_name_plural = "Expert_Product_Categories"


  def __str__(self):
      return self.name


class Pitems(models.Model):
  name = models.CharField(max_length=255)
  category = models.ForeignKey(Pcategories, on_delete=models.SET_NULL, blank=True, null=True)
  description = models.TextField(default='None')
  price = models.DecimalField(default=0,max_digits = 10,decimal_places = 2)
  expert = models.ForeignKey(PartnerMeta, on_delete=models.SET_NULL, blank=True, null=True)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Pitems"
        verbose_name_plural = "Partner_Products"

  def __str__(self):
      return self.name

class Peimages(models.Model):
  product = models.ForeignKey(Pitems, on_delete=models.SET_NULL, blank=True, null=True)
  cover = models.ImageField(default='products/none.png', upload_to='products/')
  status = models.BooleanField(default=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Peimages"
        verbose_name_plural = "Partner_Products_Images"
  
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
    super(Peimages, self).save(*args, **kwargs)
    

  def __str__(self):
      return self.product



class Milestones(models.Model):
  name = models.CharField(max_length=255)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Milestones"
        verbose_name_plural = "Milestones"

class Quotations(models.Model):
  serial = models.CharField(default='None',unique=False, max_length=255)
  job = models.ForeignKey("core.jobs", on_delete=models.SET_NULL, blank=True, null=True)
  labour = models.DecimalField(max_digits = 10,decimal_places = 2)
  total = models.DecimalField(max_digits = 10,decimal_places = 2)
  is_active = models.BooleanField(default=True)
  is_selected = models.BooleanField(default=False)
  is_rejected = models.BooleanField(default=False)
  is_approved = models.BooleanField(default=False)
  is_completed = models.BooleanField(default=False)
  is_viewed = models.BooleanField(default=False)
  expert = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Quotations"
        verbose_name_plural = "Expert_Quotations"

class Quote_items(models.Model):
  serial = models.CharField(default='None',unique=False, max_length=255)
  quote = models.ForeignKey(Quotations, on_delete=models.SET_NULL, blank=True, null=True)
  name = models.CharField(max_length=255)
  quantity = models.IntegerField(default=0)
  price = models.DecimalField(max_digits = 10,decimal_places = 2)
  total = models.DecimalField(max_digits = 10,decimal_places = 2)
  expert = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Quote_items"
        verbose_name_plural = "Quote_items"


class Quote_milestones(models.Model):
  serial = models.CharField(default='None',unique=False, max_length=255)
  quote = models.ForeignKey(Quotations, on_delete=models.SET_NULL, blank=True, null=True)
  milestone = models.ForeignKey(Milestones, on_delete=models.SET_NULL, blank=True, null=True)
  work = models.TextField(default='None',unique=False)
  fee = models.DecimalField(max_digits = 10,default=0,unique=False,decimal_places = 2)
  pcode = models.CharField(null=True,unique=False, max_length=255)
  is_completed = models.BooleanField(default=False)
  is_approved = models.BooleanField(default=False)
  is_active = models.BooleanField(default=False)
  is_paid = models.BooleanField(default=False)
  expert = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "Quote_milestones"
        verbose_name_plural = "Quote_Milestones"



class ExpertCats(models.Model):
  name = models.CharField(max_length=255)
  cover = models.ImageField(default='cats/none.png', upload_to='cats/')
  description = models.TextField(default='None',unique=False)
  status = models.BooleanField(default=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "ExpertCats"
        verbose_name_plural = "Expert_Categories"

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
    super(ExpertCats, self).save(*args, **kwargs)


  def __str__(self):
      return self.name



class ExpertSkills(models.Model):
  category = models.ForeignKey(ExpertCats, on_delete=models.SET_NULL, blank=True, null=True)
  name = models.CharField(max_length=255)
  cover = models.ImageField(default='cats/none.png', upload_to='cats/')
  status = models.BooleanField(default=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "ExpertSkills"
        verbose_name_plural = "Expert_Skills"

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
    super(ExpertSkills, self).save(*args, **kwargs)

  def __str__(self):
      return self.name
        