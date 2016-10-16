from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import IesImport


@receiver(pre_delete, sender=IesImport)
def iesimport_pre_delete(sender, **kwargs):
    instance = kwargs['instance']
    instance.ifile.delete(False)
