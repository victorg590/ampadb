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
    instance = kwargs['instance']
    profile = Profile.objects.get_or_create(alumne=instance)[0]
    if profile.user:
        profile.user.email = instance.correu_alumne
        profile.user.first_name = instance.nom
        profile.user.last_name = instance.cognoms
        profile.user.save()


@receiver(pre_save, sender=Classe)
def classe_pre_save(sender, **kwargs):
    signal_clean(sender, **kwargs)
