from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .forms import *
from .models import *
from django.contrib.auth.models import User
from contactboard.models import Alumne
from ampadb.support import is_admin, gen_username, gen_codi
from django.contrib.auth.decorators import login_required, user_passes_test
import csv
import weasyprint
from django.views.decorators.debug import (sensitive_variables,
    sensitive_post_parameters)

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
            user = User.objects.create_user(cdata['username'],
                password=cdata['password'])
            user.is_staff = True
            user.is_superuser = True
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
        form = UsersForms.NewForm(initial={'alumne': alumne,
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
        'unregistered': uu,
        'registered': users
    }
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
