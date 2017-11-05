import datetime
import json
import logging
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.debug import (sensitive_variables,
                                           sensitive_post_parameters)
from ampadb.support import is_admin, redirect_with_get
from contactboard.models import Classe, Alumne
from .forms import ExportForm, ImportForm, IEFormats
from . import export_fmts as exf
from . import import_fmts as imf
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
        'form': ExportForm(initial={'classe': classe_id}, auto_id='%s'),
        'today': datetime.datetime.today().strftime('%Y-%m-%d')
    }
    return render(request, 'importexport/export.html', context)


# pylint: disable=too-many-branches,too-many-statements
@login_required
@user_passes_test(is_admin)
@sensitive_post_parameters('contrasenya', 'repeteix_la_contrasenya')
@sensitive_variables('password')
def genexport(request):
    form = ExportForm(request.POST)
    if not form.is_valid():
        return redirect('importexport:export')
    try:
        dformat = IEFormats(form.cleaned_data['format'])
        # ^ Conflicte amb built-in format()
    except ValueError as ex:
        logging.warning("S'ha intentat exportar al format invàlid %s", ex)
        return redirect('importexport:export')
    if form.cleaned_data['classe']:
        classe_id = form.cleaned_data['classe']
        classe = get_object_or_404(Classe, id_interna=classe_id)
    else:
        classe = None
    password = form.cleaned_data['contrasenya']
    if dformat == IEFormats.CSV:
        if classe:
            filename = classe.id_interna + '.csv'
            alumnes = Alumne.objects.filter(classe=classe)
        else:
            filename = 'alumnes.csv'
            alumnes = Alumne.objects.all()
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = (
            'attachment; filename="{}"'.format(filename))
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
        response['Content-Disposition'] = (
            'attachment; filename="{}"'.format(filename))
        exf.export_ampacsv(response, alumnes)
        return response
    elif dformat == IEFormats.JSON:
        if classe:
            filename = classe.id_interna + '.json'
        else:
            filename = datetime.datetime.today().strftime('%Y-%m-%d') + '.json'
        response = HttpResponse(content_type="application/json")
        response['Content-Disposition'] = (
            'attachment; filename="{}"'.format(filename))
        exf.export_json(response, classe)
        return response
    elif dformat == IEFormats.PICKLE:
        if classe:
            filename = classe.id_interna + '.pkl.gz'
        else:
            filename = (
                datetime.datetime.today().strftime('%Y-%m-%d') + '.pkl.gz')
        if password:
            filename += '.aes'
        response = HttpResponse(content_type="application/gzip")
        response['Content-Disposition'] = (
            'attachment; filename="{}"'.format(filename))
        if password:
            exf.export_encrypted_pickle(response, password, classe)
        else:
            exf.export_pickle(response, classe)
        return response


# pylint: enable=too-many-branches,too-many-statements


@login_required
@user_passes_test(is_admin)
def import_view(request):
    error_text = request.GET.get('error_text')
    print(error_text)
    context = {
        'error_text': error_text,
        'form': ImportForm(auto_id="%s"),
        'extensions':
        json.dumps({str(k): v
                    for k, v in imf.EXTENSIONS.items()})
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
            return redirect_with_get(
                'importexport:import',
                [('error_text', 'No es pot detectar el format')])
    else:
        dformat = fformat
    preexistents = form.cleaned_data['preexistents']
    password = form.cleaned_data['contrasenya']
    try:
        if dformat == IEFormats.AMPACSV:
            text = imf.bytestream_to_text(
                request.FILES['ifile'], encoding=(request.encoding or 'utf-8'))
            ampacsv.import_ampacsv(text, preexistents)
        elif dformat == IEFormats.EXCELCSV:
            text = imf.bytestream_to_text(
                request.FILES['ifile'], encoding=(request.encoding or 'utf-8'))
            ampacsv.import_excel(text, preexistents)
        elif dformat == IEFormats.PICKLE:
            imf.import_pickle(request.FILES['ifile'], password, preexistents)
        elif dformat == IEFormats.JSON:
            text = imf.bytestream_to_text(
                request.FILES['ifile'], encoding=(request.encoding or 'utf-8'))
            imf.import_json(text, preexistents)
        return redirect('contactboard:adminlist')
    except ampacsv.InvalidFormat as ex:
        return redirect_with_get('importexport:import',
                                 [('error_text', str(ex))])


# Tot i que no està enllaçat, l'accés a aquesta pàgina no és un risc
def format_view(request):
    return render(request, 'importexport/format.html')


def download_template(_):  # No importa l'argument `request`
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="template.csv"'
    ampacsv.get_template(response)
    return response
