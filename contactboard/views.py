from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from ampadb.support import is_admin
from usermanager.models import Profile

from .models import Curs, Classe, Alumne
from .forms import (CursForms, ClasseForms, AlumneForms, MailtoForm,
                    MailtoClasseForm)


# Conflicte amb la funció built-in list()
@login_required
def list_view(request, id_classe):
    classe = get_object_or_404(Classe, id_interna=id_classe)
    context = {
        'classe': classe,
        'alumnes': Alumne.objects.filter(classe=classe),
    }
    return render(request, 'contactboard/list.html', context)


@login_required
@user_passes_test(is_admin)
def adminlist(request):
    cursos = Curs.objects.all().order_by('ordre')
    classes = Classe.objects.all().order_by('curs')
    context = {'cursos': cursos, 'classes': classes}
    return render(request, 'contactboard/adminlist.html', context)


@login_required
@user_passes_test(is_admin)
def add_classe(request, id_curs):
    curs = get_object_or_404(Curs, id_interna=id_curs)
    if request.method == 'POST':
        form = ClasseForms.NewForm(request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            classe = Classe()
            classe.nom = cdata['nom']
            classe.id_interna = cdata['id_interna']
            classe.curs = curs
            classe.save()
            return redirect('contactboard:adminlist')
    else:
        form = ClasseForms.NewForm(initial={'curs': curs})
    context = {'form': form, 'submitText': 'Crear'}
    return render(request, 'contactboard/add.html', context)


@login_required
@user_passes_test(is_admin)
def edit_classe(request, id_classe):
    classe = get_object_or_404(Classe, id_interna=id_classe)
    if request.method == 'POST':
        form = ClasseForms.EditForm(request.POST)
        if form.is_valid():
            if form.has_changed:
                cdata = form.cleaned_data
                classe.nom = cdata['nom']
                classe.curs = cdata['curs']
                classe.save()
            return redirect('contactboard:adminlist')
    else:
        classe_initial = {
            'nom': classe.nom,
            'id_interna': classe.id_interna,
            'curs': classe.curs.id_interna
        }
        form = ClasseForms.EditForm(classe, initial=classe_initial)
    context = {'form': form, 'submitText': 'Editar'}
    return render(request, 'contactboard/add.html', context)


@login_required
@user_passes_test(is_admin)
def delete_classe(request, id_classe):
    classe = get_object_or_404(Classe, id_interna=id_classe)
    if request.method == 'POST':
        classe.delete()
        return redirect('contactboard:adminlist')
    context = {'classe': classe}
    return render(request, 'contactboard/delete-classe.html', context)


@login_required
@user_passes_test(is_admin)
def add_curs(request):
    if request.method == "POST":
        form = CursForms.NewForm(request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            curs = Curs()
            curs.nom = cdata['nom']
            curs.id_interna = cdata['id_interna']
            if cdata['ordre']:
                curs.ordre = cdata['ordre']
            curs.save()
            return redirect('contactboard:adminlist')
    else:
        form = CursForms.NewForm()
    context = {'form': form, 'submitText': 'Crear'}
    return render(request, 'contactboard/add.html', context)


@login_required
@user_passes_test(is_admin)
def edit_curs(request, id_curs):
    curs = get_object_or_404(Curs, id_interna=id_curs)
    if request.method == 'POST':
        form = CursForms.EditForm(request.POST)
        if form.is_valid():
            if form.has_changed:
                cdata = form.cleaned_data
                curs.nom = cdata['nom']
                curs.ordre = cdata['ordre']
            return redirect('contactboard:adminlist')
    else:
        curs_initial = {
            'nom': curs.nom,
            'id_interna': curs.id_interna,
            'ordre': curs.ordre
        }
        form = CursForms.EditForm(curs, initial=curs_initial)
    context = {'form': form, 'submitText': 'Editar'}
    return render(request, 'contactboard/add.html', context)


@login_required
@user_passes_test(is_admin)
def delete_curs(request, id_curs):
    curs = get_object_or_404(Curs, id_interna=id_curs)
    if request.method == 'POST':
        curs.delete()
        return redirect('contactboard:adminlist')
    context = {'curs': curs, 'classes': Classe.objects.filter(curs=curs)}
    return render(request, 'contactboard/delete-curs.html', context)


@login_required
@user_passes_test(is_admin)
def add_alumne(request, id_classe):
    classe = get_object_or_404(Classe, id_interna=id_classe)
    if request.method == 'POST':
        form = AlumneForms.NewForm(request.POST)
        if form.is_valid():
            alumne = form.save(commit=False)
            alumne.classe = classe
            alumne.save()
            return redirect('contactboard:list', id_classe)
    else:
        form = AlumneForms.NewForm()
    context = {'form': form, 'classe': classe, 'submitText': 'Afegir'}
    return render(request, 'contactboard/add.html', context)


@login_required
def edit_alumne(request, alumne_pk):
    if not is_admin(request.user):
        profile = Profile.objects.get(user=request.user)
        if profile.alumne.pk != int(alumne_pk):
            return redirect('contactboard:edit-alumne', profile.alumne.pk)

    alumne = get_object_or_404(Alumne, pk=alumne_pk)
    if request.method == 'POST':
        if is_admin(request.user):
            form = AlumneForms.AdminEditForm(request.POST, instance=alumne)
        else:
            form = AlumneForms.EditForm(request.POST, instance=alumne)
        if form.is_valid():
            if form.has_changed():
                form.save()
            return redirect('contactboard:list', alumne.classe.id_interna)
    else:
        if is_admin(request.user):
            form = AlumneForms.AdminEditForm(instance=alumne)
        else:
            form = AlumneForms.EditForm(
                instance=alumne, initial={
                    'classe': alumne.classe
                })
    context = {
        'form': form,
        'submitText': 'Actualitzar',
        'info_compartir': True
    }
    return render(request, 'contactboard/add.html', context)


@login_required
@user_passes_test(is_admin)
def delete_alumne(request, alumne_pk):
    alumne = get_object_or_404(Alumne, pk=alumne_pk)
    if request.method == 'POST':
        try:
            profile = Profile.objects.get(alumne=alumne)
            if profile.user:
                profile.user.delete()
            if profile.unregisteredUser:
                profile.unregisteredUser.delete()
            profile.delete()
        except Profile.DoesNotExist:
            pass
        alumne.delete()
        return redirect('contactboard:list', alumne.classe.id_interna)
    context = {'alumne': alumne}
    return render(request, 'contactboard/delete-alumne.html', context)


def _build_mailto(fdata, classe=None):
    if classe:
        fdata['classes'] = [classe]
    mailto_str = 'mailto:'
    if fdata['enviar_com'] == MailtoForm.AS_BCC:
        mailto_str += '?bcc='
    for classe_id in fdata['classes']:
        classe = Classe.objects.get(id_interna=classe_id)
        for alumne in Alumne.objects.filter(classe=classe):
            if (MailtoForm.TO_ALUMNES in fdata['enviar_a']
                    and alumne.correu_alumne):
                mailto_str += alumne.correu_alumne + ','
            if MailtoForm.TO_TUTORS in fdata['enviar_a']:
                if alumne.correu_tutor_1:
                    mailto_str += alumne.correu_tutor_1 + ','
                if alumne.correu_tutor_2:
                    mailto_str += alumne.correu_tutor_2 + ','
    while mailto_str[-1] == ',':
        mailto_str = mailto_str[:-1]
    return mailto_str


@login_required
@user_passes_test(is_admin)
def mailto(request):
    if request.method == 'POST':
        form = MailtoForm(request.POST)
        if form.is_valid():
            response = HttpResponse()
            response.write(
                '<meta http-equiv="refresh" content="0; url={}" />'.format(
                    _build_mailto(form.cleaned_data)))
            return response
    else:
        form = MailtoForm()
    context = {'form': form}
    return render(request, 'contactboard/mailto.html', context)


@login_required
@user_passes_test(is_admin)
def mailtoclasse(request, id_classe):
    classe = get_object_or_404(Classe, id_interna=id_classe)
    if request.method == 'POST':
        form = MailtoClasseForm(request.POST)
        if form.is_valid():
            response = HttpResponse()
            response.write(
                '<meta http-equiv="refresh" content="0; url={}" />'.format(
                    _build_mailto(form.cleaned_data, id_classe)))
            return response
    else:
        form = MailtoClasseForm()
    context = {'form': form, 'classe': classe}
    return render(request, 'contactboard/mailto.html', context)
