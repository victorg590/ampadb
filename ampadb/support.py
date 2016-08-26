from django.http import HttpResponseRedirect
from urllib.parse import quote
from usermanager.models import User, UnregisteredUser
import logging
import random

def is_admin(user):
    return user.is_staff and user.is_superuser

def context_processor(request):
    user = request.user
    if not user.is_authenticated():
        return {'admin': False}
    return {'admin': is_admin(user)}


def redirect_with_get(url, get_params, *args, **kwargs):
    """Crea una redirecció amb paràmetres GET.

    Demana una URL que es passa a `reverse` (amb arguments, si cal)
    i una llista de tuples del format `(clau, valor)`. Els valors seràn escapats
    per a URL.
    """
    first = True
    get_string = ''
    for t in get_params:
        if first:
            get_string += '?{}={}'.format(t[0], quote(t[1]))
            first = False
        else:
            get_string += '&{}={}'.format(t[0], quote(t[1]))
    resolved_url = reverse(url, args=args, kwargs=kwargs)
    return HttpResponseRedirect(resolved_url + get_string)

def username_exists(username):
    return (User.objects.filter(username=username) or
        UnregisteredUser.objects.filter(username=username))

def get_user(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
            user = UnregisteredUser.objects.get(username=username)
    return user

def gen_username(alumne):
    try:
        un = alumne.nom.replace(' ', '')[0]
    except IndexError:
        return ''
    un += '.'
    un += alumne.cognoms
    un = un.replace(' ', '')
    un = un.lower()
    next_try = 1
    while True:
        if not username_exists(un):
            break
        next_try_str = str(next_try)
        un = un[:(30 - len(next_try_str))] + next_try_str
        next_try += 1
        if next_try > 50:
            logging.warning('Unable to find a new username')
            return None
    return un[:30]

def gen_codi():
    try:
        ransrc = random.SystemRandom()
    except NotImplementedError:
        ransrc = random
    num = ransrc.randint(000000, 999999)
    return str(num).zfill(6)

def signal_clean(sender, **kwargs):
    instance = kwargs['instance']
    return instance.full_clean()
