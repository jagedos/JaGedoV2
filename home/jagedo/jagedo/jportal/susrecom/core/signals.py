from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os
from .models import PCarts

@receiver(pre_delete, sender=PCarts)
def pcart_pre_delete_handler(sender, instance, **kwargs):
    # Pass False so FileField doesn't save the model.
    if instance.doc:
        if os.path.isfile(instance.doc.path):
            os.remove(instance.doc.path)