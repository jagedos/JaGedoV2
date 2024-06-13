from django.db import models


# Create your models here.
class Counties(models.Model):
  name = models.CharField(max_length=255)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.name

  class Meta:
        verbose_name = "Counties"
        verbose_name_plural = "Counties"



class PickUps(models.Model):
  county = models.ForeignKey(Counties, on_delete=models.SET_NULL, blank=True, null=True)
  name = models.CharField(max_length=255)
  status = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "PickUps"
        verbose_name_plural = "Pickup_Points"

class CartMeta(models.Model):
  admin = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, blank=True, null=True)
  customer = models.ForeignKey("accounts.CustomUser",related_name="mcustomer", on_delete=models.SET_NULL, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
        verbose_name = "CartMeta"
        verbose_name_plural = "Cart_Meta"

# create model for saving type legal documents
class LegalDocumentTypes(models.Model):
    name = models.CharField(max_length=255)
    is_global = models.BooleanField(default=True)
    is_customer = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "LegalDocumentTypes"
        verbose_name_plural = "Legal_Document_Types"
    
    def __str__(self):
        return self.name

# create model for saving legal documents e.g. terms and conditions, privacy policy, etc
class LegalDocuments(models.Model):
    type = models.ForeignKey(LegalDocumentTypes, on_delete=models.SET_NULL, blank=True, null=True)
    document = models.FileField(upload_to='documents/')
    status = models.BooleanField(default=True)
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "LegalDocuments"
        verbose_name_plural = "Legal_Documents"



class SMS(models.Model):
    message = models.TextField()
    to_all = models.BooleanField(default=False)
    to_customer = models.BooleanField(default=False)
    to_vendor = models.BooleanField(default=False)
    to_manager = models.BooleanField(default=False)
    to_partner = models.BooleanField(default=False)
    receipient = models.ForeignKey("accounts.CustomUser", related_name="receipient" , on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
# system modules
class Modules(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modules"
        verbose_name_plural = "Modules"

    def __str__(self):
        return self.name


# module actions
class Actions(models.Model):
    name = models.CharField(max_length=255)
    module = models.ForeignKey(
        Modules, default=1, on_delete=models.SET_NULL, blank=True, null=True
    )
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Actions"
        verbose_name_plural = "Actions"

    def __str__(self):
        return self.name


# create user types model
class UserTypes(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "UserTypes"
        verbose_name_plural = "UserTypes"

    def __str__(self):
        return self.name


# system permissions
class Permissions(models.Model):
    user_type = models.ForeignKey(
        UserTypes, on_delete=models.SET_NULL, blank=True, null=True
    )
    action = models.ForeignKey(
        Actions, on_delete=models.SET_NULL, blank=True, null=True
    )
    status = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        unique_together = [
            "user_type",
            "action",
        ]  # <-- This line enforces the unique constraint

    def __str__(self):
        return self.action.name


    






