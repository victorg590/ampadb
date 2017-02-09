from django.http import HttpResponse, JsonResponse, Http404
from django.utils.html import mark_safe
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from .forms import *
from .models import *
from django.contrib.auth.models import User
from contactboard.models import Alumne
from ampadb.support import is_admin, gen_username, gen_codi
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query_utils import Q
import csv
import json
import weasyprint
from django.views.decorators.debug import (sensitive_variables,
                                           sensitive_post_parameters)
from ampadb_index.parse_md import parse_md


@sensitive_post_parameters('password', 'password_confirm')
@sensitive_variables('form', 'cdata')
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            uu = UnregisteredUser.objects.get(username=cdata['username'])
            profile = Profile.objects.get(unregisteredUser=uu)
            user = User.objects.create_user(uu.username,
                                            password=cdata['password'])
            user.save()
            profile.unregisteredUser = None
            profile.user = user
            profile.save()
            uu.delete()
            profile.alumne.save()
            return redirect('login')
    else:
        form = RegisterForm()
    context = {
        'form': form
    }
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
                cdata['username'], password=cdata['password'],
                email=cdata['email'])
            user.save()
            return redirect('usermanager:list')
    else:
        form = UsersForms.NewAdminForm()
    context = {
        'form': form
    }
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
            uu = UnregisteredUser(username=cdata['username'],
                                  codi=cdata['codi'])
            uu.save()
            try:
                p = Profile.objects.get(alumne=alumne)
                p.unregisteredUser = uu
            except Profile.DoesNotExist:
                p = Profile(alumne=alumne, unregisteredUser=uu)
            p.save()
            return redirect('contactboard:list', alumne.classe.id_interna)
    else:
        form = UsersForms.NewForm(initial={
            'alumne': alumne,
            'username': gen_username(alumne)})
    context = {
        'form': form
    }
    return render(request, 'usermanager/new.html', context)


@login_required
@user_passes_test(is_admin)
def list_users(request):
    uu = UnregisteredUser.objects.all()
    users = User.objects.all()
    context = {
        'n_unregistered': uu.count(),
        'n_registered': users.count(),
        'max_display': 10
    }
    context['unregistered'] = mark_safe(json.dumps(API._gen_json_unreg(uu))) \
        if context['n_unregistered'] <= context['max_display'] else 'null'
    context['registered'] = mark_safe(json.dumps(API._gen_json_reg(users))) \
        if context['n_registered'] <= context['max_display'] else 'null'
    return render(request, 'usermanager/list.html', context)


@login_required
@user_passes_test(is_admin)
def delete_user(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        try:
            p = Profile.objects.get(user=user)
            p.delete()
        except Profile.DoesNotExist:
            pass
        user.delete()
        return redirect('usermanager:list')
    context = {
        'tuser': user
    }
    return render(request, 'usermanager/delete.html', context)


@login_required
@user_passes_test(is_admin)
def cancel_user(request, username):
    uu = get_object_or_404(UnregisteredUser, username=username)
    if request.method == 'POST':
        try:
            p = Profile.objects.get(unregisteredUser=uu)
            p.delete()
        except Profile.DoesNotExist:
            pass
        uu.delete()
        return redirect('usermanager:list')
    context = {
        'tuser': uu
    }
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
    context = {
        'tuser': user,
        'form': form
    }
    return render(request, 'usermanager/changepassword.html', context)


@login_required
@user_passes_test(is_admin)
def change_code_auto(request, username):
    uu = get_object_or_404(UnregisteredUser, username=username)
    uu.codi = gen_codi()
    uu.save()
    return redirect('usermanager:list')


@login_required
@user_passes_test(is_admin)
def change_code(request, username):
    uu = get_object_or_404(UnregisteredUser, username=username)
    if request.method == 'POST':
        form = ChangeCodeForm(request.POST)
        if form.is_valid():
            uu.codi = form.cleaned_data['codi']
            uu.save()
            return redirect('usermanager:list')
    else:
        form = ChangeCodeForm()
    context = {
        'form': form,
        'tuser': uu
    }
    return render(request, 'usermanager/change_code.html', context)


class _MockAlumne:
    def __init__(self):
        self.nom = ''
        self.cognoms = ''

    def __str__(self):
        return self.nom + self.cognoms


@login_required
@user_passes_test(is_admin)
def export_uu(request):
    uu = UnregisteredUser.objects.all()
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.DictWriter(response, ['Nom', 'Usuari', 'Codi'])
    writer.writeheader()
    for u in uu:
        try:
            alumne = Profile.objects.get(unregisteredUser=u).alumne
        except Profile.DoesNotExist:
            alumne = _MockAlumne()
        writer.writerow({'Nom': str(alumne), 'Usuari': u.username,
                         'Codi': u.codi})
    return response


@login_required
@user_passes_test(is_admin)
def print_uu(_):
    classes = {}
    for uu in UnregisteredUser.objects.all():
        classe = Profile.objects.get(unregisteredUser=uu).alumne.classe
        try:
            classes[classe].append(uu)
        except KeyError:
            classes[classe] = [uu]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="codis_ampa.pdf"'
    template = loader.get_template('usermanager/pdf_codis.html')
    html = template.render({'classes': [(k, classes[k]) for k in classes]})
    weasyprint.HTML(string=html).write_pdf(response)
    return response


def _letter(request, template):
    context = {
        'tpl': mark_safe(parse_md(template, wrap='raw')),
        'uu': UnregisteredUser.objects.all(),
        'surl': request.build_absolute_uri('/')
    }
    return render(request, 'usermanager/pdf_letter.html', context)


@login_required
@user_passes_test(is_admin)
def gen_letter(request):
    INITIAL = '''\
        Alumne/a: $nom $cognoms

        Usuari: $usuari

        Codi: $codi

        Lloc web: $url'''
    INITIAL = '\n'.join([s.strip() for s in INITIAL.split('\n')])
    if request.method == 'POST':
        form = LetterForm(request.POST, initial={'plantilla': INITIAL})
        if form.is_valid():
            return _letter(request, form.cleaned_data['plantilla'])
    else:
        form = LetterForm(initial={'plantilla': INITIAL})
    context = {
        'form': form
    }
    return render(request, 'usermanager/gen_letter.html', context)


class API:
    # Crea decoradors que tornin un error 403 Forbidden en lloc d'una
    # redirecció
    def raw_login_required(fn):  # pylint: disable=no-self-argument
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            return fn(request, *args, **kwargs)  # pylint: disable=not-callable
        return wrapper

    def raw_user_passes_test(test):  # pylint: disable=no-self-argument
        def decorator(fn):
            def wrapper(request, *args, **kwargs):
                if not test(request.user):  # pylint: disable=not-callable
                    raise PermissionDenied
                return fn(request, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def _gen_json_reg(users):
        ret = []
        for u in users:
            try:
                alumne = u.profile.alumne
                alumne_url = alumne.get_absolute_url()
            except ObjectDoesNotExist:
                alumne = None
                alumne_url = None
            ret.append({
                'alumne': str(alumne) if alumne is not None else None,
                'alumneUrl': alumne_url,
                'username': u.username,
                'admin': is_admin(u),
                'changePasswordUrl':
                    reverse('usermanager:admin-changepassword',
                            args=[u.username]),
                'deleteUrl': reverse('usermanager:delete',
                                     args=[u.username])
            })
        return ret

    def _gen_json_unreg(users):
        ret = []
        for u in users:
            ret.append({
                # Assumeix que tots els UU tenen un usuari associat
                'alumne': str(u.profile.alumne),
                'alumneUrl': u.profile.alumne.get_absolute_url(),
                'username': u.username,
                'codi': u.codi,
                'changeAutoUrl': reverse('usermanager:change-code-auto',
                                         args=[u.username]),
                'changeUrl': reverse('usermanager:change-code',
                                     args=[u.username]),
                'cancelUrl': reverse('usermanager:cancel', args=[u.username])
            })
        return ret

    @staticmethod
    @raw_login_required
    @raw_user_passes_test(is_admin)
    def registered_users(request):
        data = {'registeredUsers': API._gen_json_reg(User.objects.all())}
        return JsonResponse(data)

    @staticmethod
    @raw_login_required
    @raw_user_passes_test(is_admin)
    def unregistered_users(request):
        data = {'unregisteredUsers': API._gen_json_unreg(
            UnregisteredUser.objects.all()
        )}
        return JsonResponse(data)

    @staticmethod
    @raw_login_required
    @raw_user_passes_test(is_admin)
    def echo(request):
        return JsonResponse(request.GET)

    @staticmethod
    @raw_login_required
    @raw_user_passes_test(is_admin)
    def search(request):
        q = request.GET.get('q')
        if q is None:
            raise Http404('Required "q" parameter')
        if not q:
            return JsonResponse(
                {'unregisteredUsers': [], 'registeredUsers': []})
        res = {}
        uu = UnregisteredUser.objects.filter(
            Q(username__icontains=q) | Q(profile__alumne__nom__icontains=q) |
            Q(profile__alumne__cognoms__icontains=q)
        )
        if uu.exists():
            res['unregisteredUsers'] = API._gen_json_unreg(uu)
        else:
            res['unregisteredUsers'] = []
        ru = User.objects.filter(
            Q(username__icontains=q) | Q(profile__alumne__nom__icontains=q) |
            Q(profile__alumne__cognoms__icontains=q)
        )
        if ru.exists():
            res['registeredUsers'] = API._gen_json_reg(ru)
        else:
            res['registeredUsers'] = []
        return JsonResponse(res)
