# pylint: disable=unused-argument
from django.db.models.signals import pre_save
from django.dispatch import receiver
from ampadb.support import signal_clean
from .models import Extraescolar, Inscripcio


@receiver(pre_save, sender=Extraescolar)
def extraescolar_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)


@receiver(pre_save, sender=Inscripcio)
def inscripcio_pre_save(sender, **kwargs):
    instance = kwargs['instance']
    if instance.activitat.preu == 0:
        instance.pagat = True
    signal_clean(sender, **kwargs)
