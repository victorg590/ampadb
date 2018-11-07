import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import mark_safe
from ampadb.support import is_admin
from contactboard.models import Classe
from .forms import Ies as Forms
from .models import IesImport, ClassMap, AddAlumne, MoveAlumne, DeleteAlumne, DeleteClasse
from . import ies_format
from .import_fmts import InvalidFormat


@login_required
@user_passes_test(is_admin)
def upload(request):
    if request.method == 'POST':
        form = Forms.UploadForm(request.POST, request.FILES)
        if form.is_valid():
            nom = form.cleaned_data['ifile'].name
            imp = IesImport.objects.create(nom_importacio=nom)
            ies_format.parse_ies_csv(form.cleaned_data['ifile'], imp)
            return redirect('importexport:ies:classnames', imp.pk)
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
    mapa_nou = None
    error_msg = (
        'Entrada invàlida. Si us plau, contacta amb el desenvolupador.'
        "Codi d'error: %s")
    if request.method == 'POST':
        try:
            mapa_nou = json.loads(request.POST.get('res', '{}'))
            print(mapa_nou)
        except json.JSONDecodeError:
            errors.append(error_msg % 'JSON invàlid')
        with transaction.atomic():
            for classe_imp, classe_bd in mapa_nou.items():
                try:
                    map_obj = ClassMap.objects.get(
                        importacio=imp, codi_classe=classe_imp)
                except ClassMap.DoesNotExist:
                    errors.append(
                        error_msg %
                        ("no existeix la classe d'importació " + classe_imp))
                    continue
                classe_obj = None
                if classe_bd is not None:
                    try:
                        classe_obj = Classe.objects.get(pk=classe_bd)
                    except Classe.DoesNotExist:
                        errors.append(
                            error_msg %
                            ("no existeix la classe de BD " + str(classe_bd)))
                        continue
                map_obj.classe_mapejada = classe_obj
                map_obj.save()
            if errors:
                transaction.rollback()
            else:
                ies_format.invalidar_canvis(imp)

    mapa_anterior = {
        classe_imp: classe_bd
        for classe_imp, classe_bd in ClassMap.objects.filter(
            importacio=imp).values_list('codi_classe', 'classe_mapejada__pk')
    }
    mapa_complet = not ClassMap.objects.filter(
        importacio=imp, classe_mapejada=None).exists()
    # Detecció de classes repetides:
    classes_repetides = {}
    for rep in ClassMap.objects.filter(
            importacio=imp, classe_mapejada__isnull=False).values_list(
                'classe_mapejada__pk', flat=True).annotate(
                    map_count=Count('codi_classe')).filter(map_count__gt=1):
        classe_mapejada = Classe.objects.get(pk=rep)
        classes_repetides[str(classe_mapejada)] = ClassMap.objects.filter(
            importacio=imp, classe_mapejada=classe_mapejada).values_list(
                'codi_classe', flat=True)

    imp_classes = [c for c in mapa_anterior]
    imp_classes.sort()
    context = {
        'mapa_anterior': mark_safe(json.dumps(mapa_anterior)),
        'mapa_complet': mapa_complet,
        'imp': imp,
        'imp_classes': imp_classes,
        'eliminar_anterior': mark_safe(json.dumps(imp.eliminar_no_mencionats)),
        'classes': Classe.objects.all().select_related(),
        'errors': errors,
        'classes_repetides': classes_repetides
    }
    return render(request, 'importexport/ies/classnames.html', context)


@login_required
@user_passes_test(is_admin)
def confirm(request, upload_id):
    imp = get_object_or_404(IesImport, pk=upload_id)
    with transaction.atomic():
        ies_format.calcular_canvis(imp)
    if request.method == 'POST':  # TODO: Només per depuració
        with transaction.atomic():
            ies_format.invalidar_canvis(imp)
    changes = {
        'add':
        AddAlumne.objects.filter(importacio=imp).select_related(
            'dada_relacionada', 'nova_classe', 'nova_classe__curs'),
        'move':
        MoveAlumne.objects.filter(importacio=imp).select_related(
            'alumne', 'alumne__classe', 'alumne__classe__curs', 'nova_classe',
            'nova_classe__curs'),
        'delete':
        DeleteAlumne.objects.filter(importacio=imp).select_related(
            'alumne', 'alumne__classe', 'alumne__classe__curs'),
        'delete_classes':
        DeleteClasse.objects.filter(importacio=imp).select_related(
            'classe', 'classe__curs')
    }
    context = {'imp': imp, 'changes': changes}
    return render(request, 'importexport/ies/confirm.html', context)


# def confirm(request, upload_id):
#     imp = get_object_or_404(IesImport, pk=upload_id)
#     try:
#         ies_format.val_json(imp.ifile, json.loads(imp.class_dict))
#     except InvalidFormat:
#         return redirect('importexport:ies:classnames', imp.pk)
#     changes = ies_format.Changes.calculate(imp.ifile,
#                                            json.loads(imp.class_dict),
#                                            imp.delete_other)
#     if request.method == 'POST':
#         with transaction.atomic():
#             changes.apply()
#             imp.delete()
#         return redirect('importexport:ies:upload')
#     context = {'imp': imp, 'chg': changes}
#     return render(request, 'importexport/ies/confirm.html', context)


@login_required
@user_passes_test(is_admin)
def cancel(request, upload_id):
    imp = get_object_or_404(IesImport, pk=upload_id)
    if request.method == 'POST':
        imp.delete()
        return redirect('importexport:ies:upload')
    context = {'imp': imp}
    return render(request, 'importexport/ies/cancel.html', context)
