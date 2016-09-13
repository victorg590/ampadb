from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Missatge
from ampadb.support import signal_clean

@receiver(pre_save, sender=Missatge)
def missatge_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)
    instance = kwargs['instance']
    if Missatge.objects.filter(pk=instance.pk).exists():
        return  # No és nou, l'ordre es el mateix que abans
    other = Missatge.objects.filter(conversacio=instance.conversacio).order_by(
        'ordre')
    if other.exists():
        instance.ordre = other.last().ordre + 1
    else:
        instance.ordre = 1
