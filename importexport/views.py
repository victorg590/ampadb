from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from ampadb.support import is_admin, redirect_with_get
from django.contrib.auth.decorators import login_required, user_passes_test
from contactboard.models import Classe, Alumne
from .forms import ExportForm, ImportForm, IEFormats
from . import export_fmts as exf
from . import import_fmts as imf
import datetime
from . import ampacsv

@login_required
@user_passes_test(is_admin)
def export_view(request, classe_id=None):
    if classe_id:
        classe = get_object_or_404(Classe, id_interna=classe_id)
    else:
        classe = None
    context = {
        'error_text': request.GET.get('error_text', ''),
        'classe': classe,
        'form': ExportForm(initial={'classe': classe_id}),
        'today': datetime.datetime.today().strftime('%Y-%m-%d')
    }
    return render(request, 'importexport/export.html', context)

@login_required
@user_passes_test(is_admin)
def genexport(request):
    form = ExportForm(request.GET)
    if not form.is_valid():
        return redirect('importexport:export')
    dformat = form.cleaned_data['format']  # Conflicte amb built-in format()
    if form.cleaned_data['classe']:
        classe_id = form.cleaned_data['classe']
        classe = get_object_or_404(Classe, id_interna=classe_id)
    else:
        classe = None
    if dformat == IEFormats.CSV:
        if classe:
            filename = classe.id_interna + '.csv'
            alumnes = Alumne.objects.filter(classe=classe)
        else:
            filename = 'alumnes.csv'
            alumnes = Alumne.objects.all()
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        exf.export_csv(response, alumnes)
        return response
    elif dformat == IEFormats.AMPACSV:
        if classe:
            filename = classe.id_interna + '.csv'
            alumnes = Alumne.objects.filter(classe=classe)
        else:
            filename = 'alumnes.csv'
            alumnes = Alumne.objects.all()
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        exf.export_ampacsv(response, alumnes)
        return response
    elif dformat == IEFormats.JSON:
        if classe:
            filename = classe.id_interna + '.json'
        else:
            filename = datetime.datetime.today().strftime('%Y-%m-%d') + '.json'
        response = HttpResponse(content_type="application/json")
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        exf.export_json(response, classe)
        return response
    elif dformat == IEFormats.PICKLE:
        if classe:
            filename = classe.id_interna + '.pkl.gz'
        else:
            filename = datetime.datetime.today().strftime('%Y-%m-%d') + \
                '.pkl.gz'
        response = HttpResponse(content_type="application/gzip")
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        exf.export_pickle(response, classe)
        return response

@login_required
@user_passes_test(is_admin)
def import_view(request):
    context = {
        'error_text': request.GET.get('error_text', ''),
        'form': ImportForm()
    }
    return render(request, 'importexport/import.html', context)

@login_required
@user_passes_test(is_admin)
def processimport(request):
    if request.method == 'GET':
        return redirect('importexport:import')
    form = ImportForm(request.POST, request.FILES)
    if not form.is_valid():
        return redirect('importexport:import')
    fformat = form.cleaned_data['format']
    if fformat == IEFormats.AUTO:
        try:
            dformat = imf.detect_format(request.FILES['ifile'].name)
        except ValueError:
            return redirect_with_get('importexport:import', [('error_text',
                'No es pot detectar el format')])
    else:
        dformat = fformat
    preexistents = form.cleaned_data['preexistents']
    try:
        if dformat == IEFormats.AMPACSV:
            text = imf.bytestream_to_text(request.FILES['ifile'],
                encoding=(request.encoding or 'utf-8'))
            imf.import_ampacsv(text, preexistents)
        elif dformat == IEFormats.EXCELCSV:
            text = imf.bytestream_to_text(request.FILES['ifile'],
                encoding=(request.encoding or 'cp1252'))  # Codificació de MS Excel
            imf.import_excel(text, preexistents)
        elif dformat == IEFormats.PICKLE:
            imf.import_pickle(request.FILES['ifile'], preexistents)
        elif dformat == IEFormats.JSON:
            text = imf.bytestream_to_text(request.FILES['ifile'], encoding=(request.encoding or 'utf-8'))
            imf.import_json(text, preexistents)
        return redirect('contactboard:adminlist')
    except imf.InvalidFormat as ex:
        return redirect_with_get('importexport:import', [('error_text',
            str(ex))])

# Tot i que no està enllaçat, l'accés a aquesta pàgina no és un risc
def format_view(request):
    return render(request, 'importexport/format.html')

def download_template(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="template.csv"'
    ampacsv.get_template(response)
    return response
