from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Alumne, Classe
from usermanager.models import Profile
from ampadb.support import signal_clean


@receiver(pre_save, sender=Alumne)
def alumne_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)


@receiver(post_save, sender=Alumne)
def alumne_post_save(sender, **kwargs):
    try:
        profile = Profile.objects.get(alumne=kwargs['instance'])
        if not profile.user:
            return
    except Profile.DoesNotExist:
        return
    instance = kwargs['instance']
    profile.user.email = instance.correu_alumne
    profile.user.first_name = instance.nom
    profile.user.last_name = instance.cognoms


@receiver(pre_save, sender=Classe)
def classe_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)
