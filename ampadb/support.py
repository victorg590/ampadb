from urllib.parse import quote
import logging
import random
import unicodedata
import re
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from usermanager.models import User, UnregisteredUser
from usermanager.models import Profile


def is_admin(user):
    return user.is_staff and user.is_superuser


def context_processor(request):
    user = request.user
    if not user.is_authenticated:
        return {'anonymous': True, 'admin': False}
    return {'anonymous': False, 'admin': is_admin(user)}


def redirect_with_get(url, get_params, *args, **kwargs):
    """Crea una redirecció amb paràmetres GET.

    Demana una URL que es passa a `reverse` (amb arguments, si cal)
    i una llista de tuples del format `(clau, valor)`. Els valors seràn
    escapats per a URL.
    """
    first = True
    get_string = ''
    for param in get_params:
        if first:
            get_string += '?{}={}'.format(param[0], quote(param[1]))
            first = False
        else:
            get_string += '&{}={}'.format(param[0], quote(param[1]))
    resolved_url = reverse(url, args=args, kwargs=kwargs)
    return HttpResponseRedirect(resolved_url + get_string)


def username_exists(username):
    return (User.objects.filter(username=username)
            or UnregisteredUser.objects.filter(username=username))


def get_user(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = UnregisteredUser.objects.get(username=username)
    return user


def gen_codi():
    try:
        ransrc = random.SystemRandom()
    except NotImplementedError:
        ransrc = random
    num = ransrc.randint(000000, 999999)
    return str(num).zfill(6)


def desaccentuar(text):
    return ''.join([
        c
        for c in unicodedata.normalize('NFKD',
                                       text)  # Descomposar: 'à' -> 'a`'
        if not unicodedata.combining(c)  # Eliminar caràcters de combinació
        # (ex. '`')
    ])


def gen_username(alumne):
    try:
        username = alumne.nom.replace(' ', '')[0]
    except IndexError:
        username = ''
    username += '.'
    username += alumne.cognoms
    username = username.replace(' ', '')
    username = username.lower()
    username = desaccentuar(username)
    un_filter = filter(
        lambda s: re.search(r'[\w.@+-]', s, flags=re.ASCII) is not None,
        username
    )  # Mira si encaixa en els caràcters ASCII. Sinó, elimina el caracter
    username = ''.join(c for c in un_filter)[:30]
    next_try = 1
    while username_exists(username):
        next_try_str = str(next_try)
        username = username[:(30 - len(next_try_str))] + next_try_str
        next_try += 1
        if next_try > 20:
            logging.warning("No s'ha pogut trobar un nom d'usuari per a %s. "
                            "Crean't-ne un aleatori.", alumne)
            return gen_codi()
    return username


def signal_clean(_, **kwargs):
    instance = kwargs['instance']
    return instance.full_clean()


def get_alumne(username):
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        try:
            uuser = UnregisteredUser.objects.get(username=username)
            profile = Profile.objects.get(unregisteredUser=uuser)
        except UnregisteredUser.DoesNotExist:
            return None
    except Profile.DoesNotExist:  # pylint: disable=duplicate-except
        return None
    return profile.alumne


class Forms:  # pylint: disable=too-few-public-methods
    class Form(forms.Form):
        required_css_class = 'required'

    class ModelForm(forms.ModelForm):
        required_css_class = 'required'
