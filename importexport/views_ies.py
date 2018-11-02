import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import mark_safe
from ampadb.support import is_admin
from contactboard.models import Classe
from .forms import Ies as Forms
from .models import IesImport
from . import ies_format
from .import_fmts import InvalidFormat


@login_required
@user_passes_test(is_admin)
def upload(request):
    if request.method == 'POST':
        form = Forms.UploadForm(request.POST, request.FILES)
        if form.is_valid():
            ins = IesImport(ifile=request.FILES['ifile'])
            ins.save()
            return redirect('importexport:ies:classnames', ins.pk)
    else:
        form = Forms.UploadForm()
    IesImport.clean_old()
    context = {'form': form, 'pending': IesImport.objects.all()}
    return render(request, 'importexport/ies/upload.html', context)


@login_required
@user_passes_test(is_admin)
def classnames(request, upload_id):
    imp = get_object_or_404(IesImport, pk=upload_id)
    errors = []
    current_valid = True
    if request.method == 'POST':
        data = {}
        try:
            data = json.loads(request.POST.get('res', ''))
            ies_format.val_json(imp.ifile, data)
        except json.JSONDecodeError:
            errors.append('Entrada invàlida, si us plau contacta amb el '
                          'desenvolupador')
            data = {}
            current_valid = False
        except InvalidFormat as ex:
            errors.append(ex)
            current_valid = False
        else:
            imp.class_dict = json.dumps(
                data, sort_keys=True, separators=(',', ':'))
            imp.eliminar_no_mencionats = json.loads(
                request.POST.get('delete', 'true'))
            imp.save()
    else:
        data = json.loads(imp.class_dict)
    all_classes = Classe.objects.all()
    imp_classes = ies_format.unique_classes(
        ies_format.parse(ies_format.validate(imp.ifile)))
    if current_valid:
        try:
            ies_format.val_json(imp.ifile, json.loads(imp.class_dict))
        except InvalidFormat:
            current_valid = False
    context = {
        'errors': errors,
        'classes': all_classes,
        'imp_classes': imp_classes,
        'pre_data': mark_safe(ies_format.rev_json(data)),
        'pre_delete': mark_safe(json.dumps(imp.eliminar_no_mencionats)),
        'current_valid': current_valid,
        'imp': imp
    }
    return render(request, 'importexport/ies/classnames.html', context)


def confirm(request, upload_id):
    imp = get_object_or_404(IesImport, pk=upload_id)
    changes = ies_format.Changes.calculate(imp)
    if request.method == 'POST':
        with transaction.atomic():
            changes.apply()
            imp.delete()
        return redirect('importexport:ies:upload')
    context = {'imp': imp, 'chg': changes}
    return render(request, 'importexport/ies/confirm.html', context)


def cancel(request, upload_id):
    imp = get_object_or_404(IesImport, pk=upload_id)
    if request.method == 'POST':
        imp.delete()
        return redirect('importexport:ies:upload')
    context = {'imp': imp}
    return render(request, 'importexport/ies/cancel.html', context)
