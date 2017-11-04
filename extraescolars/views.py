from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.debug import (sensitive_variables,
                                           sensitive_post_parameters)
from ampadb.support import get_alumne, is_admin, redirect_with_get
from .models import Extraescolar, Inscripcio
from .forms import InscripcioForm, ExtraescolarForms, SearchInscripcioForm
from .forms import InscripcioAdminForm
from .support import status_inscripcio


def check_data(request):
    alumne = get_alumne(request.user.username)
    if not alumne:
        return
    falten = []
    if not alumne.nom:
        falten.append("Nom de l'alumne")
    if not alumne.cognoms:
        falten.append("Cognoms de l'alumne")
    if not alumne.nom_tutor_1:
        falten.append("Nom del tutor 1")
    if not alumne.cognoms_tutor_1:
        falten.append("Cognoms del tutor 1")
    if not alumne.nom_tutor_2:
        falten.append("Nom del tutor 2")
    if not alumne.cognoms_tutor_2:
        falten.append("Cognoms del tutor 2")
    if falten:
        return render(request, 'extraescolars/no_data.html', {
            'falten': falten
        })
    return None


# Conflicte amb el built-in list()
@login_required
def list_view(request):
    if is_admin(request.user):
        context = {'activitats': Extraescolar.objects.all()}
        return render(request, 'extraescolars/admin-list.html', context)
    activitats = []
    alumne = get_alumne(request.user.username)
    linscripcions = []
    for extraescolar in Extraescolar.objects.all():
        extraescolar_dict = {'obj': extraescolar}
        extraescolar_dict['inscripcio_oberta'] = status_inscripcio(
            extraescolar, get_alumne(request.user.username))[0]
        activitats.append(extraescolar_dict)
        if Inscripcio.objects.filter(alumne=alumne, activitat=extraescolar):
            linscripcions.append(extraescolar)
    context = {
        'activitats': activitats,
        'inscripcions': linscripcions,
        'alumne': alumne
    }
    return render(request, 'extraescolars/list.html', context)


@login_required
def show(request, act_id):
    activitat = get_object_or_404(Extraescolar, id_interna=act_id)
    if is_admin(request.user):
        context = {
            'activitat': activitat,
            'inscripcions': Inscripcio.objects.filter(activitat=activitat)
        }
        return render(request, 'extraescolars/show.html', context)
    sinscripcio = status_inscripcio(activitat,
                                    get_alumne(request.user.username))
    context = {
        'activitat': activitat,
        'oberta': sinscripcio[0],
        'requires': sinscripcio[1]
    }
    alumne = get_alumne(request.user.username)
    try:
        ins = Inscripcio.objects.get(alumne=alumne, activitat=activitat)
        context.update({'ins': ins})
        return render(request, 'extraescolars/show_inscrit.html', context)
    except Inscripcio.DoesNotExist:
        return render(request, 'extraescolars/show_no_inscrit.html', context)


@login_required
def inscripcio(request, act_id):
    activitat = get_object_or_404(Extraescolar, id_interna=act_id)
    datacheck = check_data(request)
    if datacheck:
        return datacheck
    if (request.method != 'POST' or not status_inscripcio(
            activitat, get_alumne(request.user.username))[0]):
        return redirect('extraescolars:show', act_id)
    alumne = get_alumne(request.user.username)
    inscripcio_obj = Inscripcio()
    inscripcio_obj.activitat = activitat
    inscripcio_obj.alumne = alumne
    inscripcio_obj.confirmat = False
    inscripcio_obj.pagat = False
    inscripcio_obj.save()
    return redirect('extraescolars:show', act_id)


@login_required
def cancel(request, act_id):
    activitat = get_object_or_404(Extraescolar, id_interna=act_id)
    datacheck = check_data(request)
    if datacheck:
        return datacheck
    alumne = get_alumne(request.user.username)
    if request.method != 'POST' or not status_inscripcio(activitat, alumne)[0]:
        return redirect('extraescolars:show', act_id)
    try:
        inscripcio_obj = Inscripcio.objects.get(
            activitat=activitat, alumne=alumne)
        if not inscripcio_obj.confirmat:
            inscripcio_obj.delete()
    except Inscripcio.DoesNotExist:
        pass
    return redirect('extraescolars:show', act_id)


@sensitive_post_parameters('dni_tutor_1', 'dni_tutor_2', 'iban', 'nif_titular')
@sensitive_variables('form', 'context')
@login_required
def genfull(request):
    alumne = get_alumne(request.user.username)
    inscripcio_obj = Inscripcio.objects.filter(alumne=alumne)
    if inscripcio_obj.count() == 0:
        return redirect('extraescolars:list')
    if request.method == 'POST':
        form = InscripcioForm(request.POST)
        if form.is_valid():
            context = {
                'alumne': alumne,
                'dades': form.cleaned_data,
                'inscripcions': inscripcio_obj
            }
            return render(request, 'extraescolars/fitxa_inscripcio.html',
                          context)
    else:
        form = InscripcioForm()
    context = {'form': form}
    return render(request, 'extraescolars/genfull.html', context)


@login_required
@user_passes_test(is_admin)
def add(request):
    if request.method == 'POST':
        form = ExtraescolarForms.AddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('extraescolars:list')
    else:
        form = ExtraescolarForms.AddForm()
    context = {'form': form, 'submitText': 'Crear'}
    return render(request, 'extraescolars/add.html', context)


@login_required
@user_passes_test(is_admin)
def edit(request, act_id):
    activitat = get_object_or_404(Extraescolar, id_interna=act_id)
    if request.method == 'POST':
        form = ExtraescolarForms.EditForm(request.POST, instance=activitat)
        if form.is_valid():
            form.save()
            return redirect('extraescolars:list')
    else:
        form = ExtraescolarForms.EditForm(instance=activitat)
    context = {'form': form, 'submitText': 'Editar'}
    return render(request, 'extraescolars/add.html', context)


@login_required
@user_passes_test(is_admin)
def delete(request, act_id):
    activitat = get_object_or_404(Extraescolar, id_interna=act_id)
    if request.method == 'POST':
        activitat.delete()
        return redirect('extraescolars:list')
    context = {'extraescolar': activitat}
    return render(request, 'extraescolars/delete.html', context)


@login_required
@user_passes_test(is_admin)
def inscripcions(request):
    if request.method == 'POST':
        q = request.POST.get('q')  # pylint: disable=invalid-name
    else:
        q = request.GET.get('q')  # pylint: disable=invalid-name
    msg = request.GET.get('msg', '')
    context = {}
    if q:
        search_form = SearchInscripcioForm(request.GET)
        if search_form.is_valid():
            inscripcio_pk = search_form.cleaned_data['q']
            context['ins'] = Inscripcio.objects.get(pk=inscripcio_pk)
            if request.method == 'POST':
                form = InscripcioAdminForm(
                    request.POST, instance=context['ins'])
            else:
                form = InscripcioAdminForm(instance=context['ins'])
            if form.is_valid():
                form.save()
            context['form'] = form
    else:
        search_form = SearchInscripcioForm()
    context.update({'msg': msg, 'search_form': search_form})
    return render(request, 'extraescolars/inscripcions.html', context)


@login_required
@user_passes_test(is_admin)
def cancel_ins(request, ins_pk):
    inscripcio_obj = get_object_or_404(Inscripcio, pk=ins_pk)
    if request.method != 'POST':
        return redirect_with_get('extraescolar:inscripcions', {'q': ins_pk})
    inscripcio_obj.delete()
    return redirect_with_get('extraescolar:inscripcions', {'msg': 'deleted'})
