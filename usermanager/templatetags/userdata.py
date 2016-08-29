from django import template
from usermanager.models import Profile
from contactboard.models import Alumne
from ampadb.support import is_admin
from ampadb.support import get_alumne

register = template.Library()

register.simple_tag(get_alumne)

@register.simple_tag
def get_user(alumne_pk):
    alumne = Alumne.objects.get(pk=alumne_pk)
    try:
        profile = Profile.objects.get(alumne=alumne)
    except Profile.DoesNotExist:
        return None
    if profile.user:
        return profile.user
    elif profile.unregisteredUser:
        return profile.unregisteredUser
    else:
        return None

@register.simple_tag(name='is_admin')
def is_admin_tag(user):
    return is_admin(user)
