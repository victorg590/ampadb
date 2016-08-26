from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Alumne, Classe
from ampadb.support import signal_clean

@receiver(pre_save, sender=Alumne)
def alumne_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)

@receiver(pre_save, sender=Classe)
def classe_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)
