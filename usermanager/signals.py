from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Profile

@receiver(pre_delete, sender=Profile)
def profile_pre_delete(sender, **kwargs):
    """Eliminar l'usuari d'un perfil quan aquest s'elimina."""
    instance = kwargs['instance']
    if instance.user:
        instance.user.delete()
    if instance.unregisteredUser:
        instance.unregisteredUser.delete()
