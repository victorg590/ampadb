from django import template
from django.contrib.auth.models import User
from usermanager.models import Profile
from contactboard.models import Alumne
from ampadb.support import is_admin

register = template.Library()

@register.simple_tag
def get_alumne(username):
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        try:
            uu = UnregisteredUser.objects.get(username=username)
            profile = Profile.objects.get(unregisteredUser=uu)
        except UnregisteredUser.DoesNotExist:
            return None
    except Profile.DoesNotExist:
        return None
    return profile.alumne

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
