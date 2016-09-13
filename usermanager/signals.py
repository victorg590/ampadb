from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import Profile, UnregisteredUser
from ampadb.support import signal_clean

@receiver(pre_save, sender=Profile)
def profile_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)

@receiver(pre_delete, sender=Profile)
def profile_pre_delete(sender, **kwargs):
    """Eliminar l'usuari d'un perfil quan aquest s'elimina."""
    instance = kwargs['instance']
    if instance.user:
        instance.user.delete()
    if instance.unregisteredUser:
        instance.unregisteredUser.delete()

@receiver(pre_save, sender=UnregisteredUser)
def uu_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)
