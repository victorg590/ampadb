import csv
import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import mark_safe
from django.urls import reverse
from django.views.decorators.debug import (sensitive_variables,
                                           sensitive_post_parameters)
from ampadb.support import is_admin, gen_username, gen_codi
from ampadb.datasearch import datasearch
from ampadb_index.parse_md import parse_md
from contactboard.models import Alumne
from .forms import (RegisterForm, UsersForms, AdminChangePasswordForm,
                    ChangeCodeForm, LetterForm)
from .models import Profile, UnregisteredUser


@transaction.atomic
@sensitive_post_parameters('password', 'password_confirm')
@sensitive_variables('form', 'cdata')
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            uuser = UnregisteredUser.objects.get(username=cdata['username'])
            profile = Profile.objects.get(unregisteredUser=uuser)
            user = User.objects.create_user(
                uuser.username, password=cdata['password'])
            user.save()
            profile.unregisteredUser = None
            profile.user = user
            profile.save()
            uuser.delete()
            profile.alumne.save()
            return redirect('login')
    else:
        form = RegisterForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)


@sensitive_post_parameters('password', 'password_confirm')
@sensitive_variables('form', 'cdata')
@login_required
@user_passes_test(is_admin)
def new_admin(request):
    if request.method == "POST":
        form = UsersForms.NewAdminForm(request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            user = User.objects.create_superuser(
                cdata['username'],
                password=cdata['password'],
                email=cdata['email'])
            user.save()
            return redirect('usermanager:list')
    else:
        form = UsersForms.NewAdminForm()
    context = {'form': form}
    return render(request, 'usermanager/new_admin.html', context)


@login_required
@user_passes_test(is_admin)
def new_user(request, alumne_pk):
    alumne = get_object_or_404(Alumne, pk=alumne_pk)
    if request.method == 'POST':
        form = UsersForms.NewForm(request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            if not cdata['codi']:
                cdata['codi'] = gen_codi()
            uuser = UnregisteredUser(
                username=cdata['username'], codi=cdata['codi'])
            uuser.save()
            try:
                profile = Profile.objects.get(alumne=alumne)
                profile.unregisteredUser = uuser
            except Profile.DoesNotExist:
                profile = Profile(alumne=alumne, unregisteredUser=uuser)
            profile.save()
            return redirect('contactboard:list', alumne.classe.id_interna)
    else:
        form = UsersForms.NewForm(initial={
            'alumne': alumne,
            'username': gen_username(alumne)
        })
    context = {'form': form}
    return render(request, 'usermanager/new.html', context)


@login_required
@user_passes_test(is_admin)
def list_users(request):
    uusers = UnregisteredUser.objects.all()
    users = User.objects.all()
    context = {
        'n_unregistered': uusers.count(),
        'n_registered': users.count(),
        'max_display': 10
    }

    context['unregistered'] = 'null'
    if context['n_unregistered'] <= context['max_display']:
        context['unregistered'] = mark_safe(
            json.dumps(API.gen_json_unreg(uusers)))

    context['registered'] = 'null'
    if context['n_registered'] <= context['max_display']:
        context['registered'] = mark_safe(json.dumps(API.gen_json_reg(users)))
    return render(request, 'usermanager/list.html', context)


@login_required
@user_passes_test(is_admin)
def delete_user(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        try:
            profile = Profile.objects.get(user=user)
            profile.delete()
        except Profile.DoesNotExist:
            pass
        user.delete()
        return redirect('usermanager:list')
    context = {'tuser': user}
    return render(request, 'usermanager/delete.html', context)


@login_required
@user_passes_test(is_admin)
def cancel_user(request, username):
    uuser = get_object_or_404(UnregisteredUser, username=username)
    if request.method == 'POST':
        try:
            profile = Profile.objects.get(unregisteredUser=uuser)
            profile.delete()
        except Profile.DoesNotExist:
            pass
        uuser.delete()
        return redirect('usermanager:list')
    context = {'tuser': uuser}
    return render(request, 'usermanager/cancel.html', context)


@sensitive_post_parameters()
@sensitive_variables('form', 'cdata')
@login_required
@user_passes_test(is_admin)
def admin_changepassword(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = AdminChangePasswordForm(request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            user.set_password(cdata['password'])
            user.save()
            return redirect('usermanager:list')
    else:
        form = AdminChangePasswordForm()
    context = {'tuser': user, 'form': form}
    return render(request, 'usermanager/changepassword.html', context)


@login_required
@user_passes_test(is_admin)
def change_code_auto(_, username):
    uuser = get_object_or_404(UnregisteredUser, username=username)
    uuser.codi = gen_codi()
    uuser.save()
    return redirect('usermanager:list')


@login_required
@user_passes_test(is_admin)
def change_code(request, username):
    uuser = get_object_or_404(UnregisteredUser, username=username)
    if request.method == 'POST':
        form = ChangeCodeForm(request.POST)
        if form.is_valid():
            uuser.codi = form.cleaned_data['codi']
            uuser.save()
            return redirect('usermanager:list')
    else:
        form = ChangeCodeForm()
    context = {'form': form, 'tuser': uuser}
    return render(request, 'usermanager/change_code.html', context)


class _MockAlumne:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.nom = ''
        self.cognoms = ''

    def __str__(self):
        return self.nom + self.cognoms


@login_required
@user_passes_test(is_admin)
def export_uu(_):
    uusers = UnregisteredUser.objects.all().order_by('profile__alumne__classe',
                                                     'profile__alumne')
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.DictWriter(response, ['Nom', 'Usuari', 'Codi', 'Classe'])
    writer.writeheader()
    for uuser in uusers:
        alumne = Profile.objects.get(unregisteredUser=uuser).alumne
        writer.writerow({
            'Nom': str(alumne),
            'Usuari': uuser.username,
            'Codi': uuser.codi,
            'Classe': str(alumne.classe)
        })
    return response


@login_required
@user_passes_test(is_admin)
def print_uu(request):
    classes = {}
    for uuser in UnregisteredUser.objects.all().order_by(
            'profile__alumne__classe', 'profile__alumne'):
        classe = Profile.objects.get(unregisteredUser=uuser).alumne.classe
        try:
            classes[classe].append(uuser)
        except KeyError:
            classes[classe] = [uuser]
    return render(request, 'usermanager/pdf_codis.html', {
        'classes': classes.items()
    })


def _letter(request, template):
    context = {
        'tpl':
        mark_safe(parse_md(template, wrap='raw')),
        'uu':
        UnregisteredUser.objects.all().order_by('profile__alumne__classe',
                                                'profile__alumne'),
        'surl':
        request.build_absolute_uri('/')
    }
    return render(request, 'usermanager/letter.html', context)


@login_required
@user_passes_test(is_admin)
def gen_letter(request):
    initial = '''\
        Alumne/a: $nom $cognoms

        Usuari: `$usuari`

        Codi: `$codi`

        Lloc web: `$url`'''
    initial = '\n'.join(s.strip() for s in initial.split('\n'))
    if request.method == 'POST':
        form = LetterForm(request.POST, initial={'plantilla': initial})
        if form.is_valid():
            return _letter(request, form.cleaned_data['plantilla'])
    else:
        form = LetterForm(initial={'plantilla': initial})
    context = {'form': form}
    return render(request, 'usermanager/gen_letter.html', context)


class API:
    # Crea decoradors que tornin un error 403 Forbidden en lloc d'una
    # redirecció

    class _Access:
        @staticmethod
        def raw_login_required(fun):
            def wrapper(request, *args, **kwargs):
                if not request.user.is_authenticated:
                    raise PermissionDenied
                return fun(request, *args, **kwargs)  # pylint: disable=not-callable

            return wrapper

        @staticmethod
        def raw_user_passes_test(test):
            def decorator(fun):
                def wrapper(request, *args, **kwargs):
                    if not test(request.user):  # pylint: disable=not-callable
                        raise PermissionDenied
                    return fun(request, *args, **kwargs)

                return wrapper

            return decorator

    @staticmethod
    def gen_json_reg(users):
        ret = []
        for user in users:
            try:
                alumne = user.profile.alumne
                alumne_url = alumne.get_absolute_url()
            except ObjectDoesNotExist:
                alumne = None
                alumne_url = None
            ret.append({
                'alumne':
                str(alumne) if alumne is not None else None,
                'alumneUrl':
                alumne_url,
                'username':
                user.username,
                'admin':
                is_admin(user),
                'changePasswordUrl':
                reverse(
                    'usermanager:admin-changepassword', args=[user.username]),
                'deleteUrl':
                reverse('usermanager:delete', args=[user.username])
            })
        return ret

    @staticmethod
    def gen_json_unreg(users):
        ret = []
        for user in users:
            ret.append({
                # FIXME: Assumeix que tots els UU tenen un alumne associat
                'alumne':
                str(user.profile.alumne),
                'alumneUrl':
                user.profile.alumne.get_absolute_url(),
                'username':
                user.username,
                'codi':
                user.codi,
                'changeAutoUrl':
                reverse('usermanager:change-code-auto', args=[user.username]),
                'changeUrl':
                reverse('usermanager:change-code', args=[user.username]),
                'cancelUrl':
                reverse('usermanager:cancel', args=[user.username])
            })
        return ret

    @staticmethod
    @_Access.raw_login_required
    @_Access.raw_user_passes_test(is_admin)
    def registered_users(_):
        data = {'registeredUsers': API.gen_json_reg(User.objects.all())}
        return JsonResponse(data)

    @staticmethod
    @_Access.raw_login_required
    @_Access.raw_user_passes_test(is_admin)
    def unregistered_users(_):
        data = {
            'unregisteredUsers':
            API.gen_json_unreg(UnregisteredUser.objects.all())
        }
        return JsonResponse(data)

    @staticmethod
    @_Access.raw_login_required
    @_Access.raw_user_passes_test(is_admin)
    def echo(request):
        return JsonResponse(request.GET)

    @staticmethod
    @_Access.raw_login_required
    @_Access.raw_user_passes_test(is_admin)
    def search(request):
        q = request.GET.get('q')  # pylint: disable=invalid-name
        if q is None:
            raise Http404('Required "q" parameter')
        if not q:
            return JsonResponse({
                'unregisteredUsers': [],
                'registeredUsers': []
            })
        res = {}

        def composer(key, exact):
            # Sempre fa cerques sense comptar majúscules
            if exact:
                return (Q(username__iexact=key)
                        | Q(profile__alumne__nom__iexact=key)
                        | Q(profile__alumne__cognoms__iexact=key))
            return (Q(username__icontains=key)
                    | Q(profile__alumne__nom__icontains=key)
                    | Q(profile__alumne__cognoms__icontains=key))

        uusers = UnregisteredUser.objects.filter(datasearch(q, composer))
        if uusers.exists():
            res['unregisteredUsers'] = API.gen_json_unreg(uusers)
        else:
            res['unregisteredUsers'] = []
        rusers = User.objects.filter(datasearch(q, composer))
        if rusers.exists():
            res['registeredUsers'] = API.gen_json_reg(rusers)
        else:
            res['registeredUsers'] = []
        return JsonResponse(res)
