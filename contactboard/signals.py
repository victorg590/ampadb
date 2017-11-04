# pylint: disable=unused-argument
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from usermanager.models import Profile
from ampadb.support import signal_clean
from .models import Alumne, Classe


@receiver(pre_save, sender=Alumne)
def alumne_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)


@receiver(post_save, sender=Alumne)
def alumne_post_save(sender, **kwargs):
    instance = kwargs['instance']
    profile = Profile.objects.get_or_create(alumne=instance)[0]
    if profile.user:
        profile.user.email = instance.correu_alumne
        if len(instance.nom) <= 30:
            profile.user.first_name = instance.nom
        else:
            profile.user.first_name = instance.nom[0:26] + '...'
        if len(instance.cognoms) <= 30:
            profile.user.last_name = instance.cognoms
        else:
            profile.user.first_name = instance.cognoms[0:26] + '...'
        profile.user.save()


@receiver(pre_save, sender=Classe)
def classe_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)
