from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Extraescolar, Inscripcio
from .forms import InscripcioForm, ExtraescolarForms, SearchInscripcioForm
from .forms import InscripcioAdminForm
from ampadb.support import get_alumne, is_admin, redirect_with_get
from .support import status_inscripcio
import weasyprint

def check_data(request):
    alumne = get_alumne(request.user.username)
    if not alumne:
        return
    falten = []
    if not alumne.nom:
        falten.append("Nom de l'alumne")
    if not alumne.cognoms:
        falten.append("Cognoms de l'alumne")
    if not alumne.nom_pare:
        falten.append("Nom del pare")
    if not alumne.cognoms_pare:
        falten.append("Cognoms del pare")
    if not alumne.nom_mare:
        falten.append("Nom de la mare")
    if not alumne.cognoms_mare:
        falten.append("Cognoms de la mare")
    if falten:
        return render(request, 'extraescolars/no_data.html', {'falten': falten})
    return None

# Conflicte amb el built-in list()
@login_required
def list_view(request):
    if is_admin(request.user):
        context = {
            'activitats': Extraescolar.objects.all()
        }
        return render(request, 'extraescolars/admin-list.html', context)
    activitats = []
    alumne = get_alumne(request.user.username)
    inscripcions = []
    for e in Extraescolar.objects.all():
        d = {'obj': e}
        d['inscripcio_oberta'] = status_inscripcio(e,
            get_alumne(request.user.username))[0]
        activitats.append(d)
        if Inscripcio.objects.filter(alumne=alumne, activitat=e):
            inscripcions.append(e)
    context = {
        'activitats': activitats,
        'inscripcions': inscripcions,
        'alumne': alumne
    }
    return render(request, 'extraescolars/list.html', context)

@login_required
def show(request, act_id):
    activitat = get_object_or_404(Extraescolar, id_interna=act_id)
    if is_admin(request.user):
        context = {
            'activitat': activitat
        }
        return render(request, 'extraescolars/show.html', context)
    inscripcio = status_inscripcio(activitat, get_alumne(request.user.username))
    context = {
        'activitat': activitat,
        'oberta': inscripcio[0],
        'requires': inscripcio[1]
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
    if (request.method != 'POST' or
        not status_inscripcio(activitat, get_alumne(request.user.username))[0]):
        return redirect('extraescolars:show', act_id)
    alumne = get_alumne(request.user.username)
    inscripcio = Inscripcio()
    inscripcio.activitat = activitat
    inscripcio.alumne = alumne
    inscripcio.confirmat = False
    inscripcio.pagat = False
    inscripcio.save()
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
        inscripcio = Inscripcio.objects.get(activitat=activitat, alumne=alumne)
        if not inscripcio.confirmat:
            inscripcio.delete()
    except Inscripcio.DoesNotExist:
        pass
    return redirect('extraescolars:show', act_id)

def _genpdf(context):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Inscripció extraescolars.pdf"'
    template = loader.get_template('extraescolars/pdf.html')
    html = template.render(context)
    weasyprint.HTML(string=html).write_pdf(response)
    return response

@login_required
def genfull(request):
    alumne = get_alumne(request.user.username)
    inscripcions = Inscripcio.objects.filter(alumne=alumne)
    if inscripcions.count() == 0:
        return redirect('extraescolars:list')
    if request.method == 'POST':
        form = InscripcioForm(request.POST)
        if form.is_valid():
            context = {
                'alumne': alumne,
                'dades': form.cleaned_data,
                'inscripcions': inscripcions
            }
            return _genpdf(context)
    else:
        form = InscripcioForm()
    context = {
        'form': form
    }
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
    context = {
        'form': form,
        'submitText': 'Crear'
    }
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
    context = {
        'form': form,
        'submitText': 'Editar'
    }
    return render(request, 'extraescolars/add.html', context)

@login_required
@user_passes_test(is_admin)
def delete(request, act_id):
    activitat = get_object_or_404(Extraescolar, id_interna=act_id)
    if request.method == 'POST':
        activitat.delete()
    else:
        context = {
            'extraescolar': activitat
        }
        return render(request, 'extraescolars/delete.html', context)

@login_required
@user_passes_test(is_admin)
def inscripcions(request):
    if request.method == 'POST':
        q = request.POST.get('q')
    else:
        q = request.GET.get('q')
    msg = request.GET.get('msg', '')
    context = {}
    if q:
        search_form = SearchInscripcioForm(request.GET)
        if search_form.is_valid():
            pk = search_form.cleaned_data['q']
            context['ins'] = Inscripcio.objects.get(pk=pk)
            if request.method == 'POST':
                form = InscripcioAdminForm(request.POST,
                    instance=context['ins'])
            else:
                form = InscripcioAdminForm(instance=context['ins'])
            if form.is_valid():
                form.save()
            context['form'] = form
    else:
        search_form = SearchInscripcioForm()
    context.update({
        'msg': msg,
        'search_form': search_form
    })
    return render(request, 'extraescolars/inscripcions.html', context)

@login_required
@user_passes_test(is_admin)
def cancel_ins(request, ins_pk):
    inscripcio = get_object_or_404(Inscripcio, pk=ins_pk)
    if request.method != 'POST':
        return redirect_with_get('extraescolar:inscripcions', {'q': ins_pk})
    inscripcio.delete()
    return redirect_with_get('extraescolar:inscripcions', {'msg': 'deleted'})
