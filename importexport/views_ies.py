import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import mark_safe
from ampadb.support import is_admin
from contactboard.models import Classe
from .forms import Ies as Forms
from .models import (IesImport, ClassMap, AddAlumne, MoveAlumne, DeleteAlumne,
                     DeleteClasse)
from .import_fmts import InvalidFormat
from . import ies_format


@login_required
@user_passes_test(is_admin)
def upload(request):
    error = False
    if request.method == 'POST':
        form = Forms.UploadForm(request.POST, request.FILES)
        if form.is_valid():
            nom = form.cleaned_data['ifile'].name
            with transaction.atomic():
                imp = IesImport.objects.create(nom_importacio=nom)
                try:
                    ies_format.parse_ies_csv(form.cleaned_data['ifile'], imp)
                except InvalidFormat as invf:
                    form.add_error('ifile', invf)
                    error = True
                    imp.delete()
            if not error:
                return redirect('importexport:ies:classnames', imp.pk)
    else:
        # Invalidem tots els canvis: si hem tornat a accedir a aquesta pàgina,
        # és probable que s'hagi modificat la base de dades i els canvis ja
        # no siguin correctes
        ies_format.invalidar_canvis_tots()
        form = Forms.UploadForm()
    IesImport.clean_old()
    context = {'form': form, 'pending': IesImport.objects.all()}
    return render(request, 'importexport/ies/upload.html', context)


# BUG: Aquest sistema pot presentar errors si es modifica la base de dades
# entre que es calculen els canvis i s'apliquen. En concret:
# - Si s'afegeixen classes (no s'autoeliminaran encara que estiguin buides)
# - Si s'afegeixen alumnes (no seràn modificats; si la seva classe és eliminada,
#   aquests també ho seràn)
# Com que són events improbables (l'administrador hauria de fer les dues accions
# alhora), he decidit que és millor ignorar-ho.
# NOTE: Si s'intenta eliminar una classe a la que s'han de moure o afegir
# alumnes, es llençarà un error de integritat, el que es traduïrà a
# "500 Server Error". No és cap error del codi, és que la acció no és permesa.


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
        except json.JSONDecodeError:
            errors.append(error_msg % 'JSON invàlid')
        with transaction.atomic():
            classes = {c.pk: c for c in Classe.objects.only('pk').order_by()}
            for class_map in ClassMap.objects.filter(
                    importacio=imp).select_related('classe_mapejada'):
                nova_classe = mapa_nou.get(class_map.codi_classe, None)
                if nova_classe is None:
                    if class_map.classe_mapejada is not None:
                        class_map.classe_mapejada = None
                        class_map.save()
                elif (class_map.classe_mapejada is None
                      or class_map.classe_mapejada.pk != nova_classe):
                    try:
                        class_map.classe_mapejada = classes[nova_classe]
                    except KeyError:
                        errors.append(error_msg %
                                      ("no existeix la classe " + nova_classe))
                    class_map.save()
            if errors:
                transaction.rollback()
            else:
                imp.eliminar_classes_buides = json.loads(
                    request.POST.get('delete_missing',
                                     imp.eliminar_classes_buides))
                if imp.canvis_calculats:
                    ies_format.invalidar_canvis(imp)
                imp.save()

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
        'mapa_anterior':
        mark_safe(json.dumps(mapa_anterior)),
        'mapa_complet':
        mapa_complet,
        'imp':
        imp,
        'imp_classes':
        imp_classes,
        'eliminar_classes_buides':
        mark_safe(json.dumps(imp.eliminar_classes_buides)),
        'classes':
        Classe.objects.all().select_related(),
        'errors':
        errors,
        'classes_repetides':
        classes_repetides
    }
    print(context)
    return render(request, 'importexport/ies/classnames.html', context)


@login_required
@user_passes_test(is_admin)
def confirm(request, upload_id):
    imp = get_object_or_404(IesImport, pk=upload_id)
    with transaction.atomic():
        ies_format.calcular_canvis(imp)
        imp.save()
    if request.method == 'POST':
        with transaction.atomic():
            ies_format.aplicar_canvis(imp)
            imp.delete()
        return redirect('importexport:ies:upload')
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


@login_required
@user_passes_test(is_admin)
def cancel(request, upload_id):
    imp = get_object_or_404(IesImport, pk=upload_id)
    if request.method == 'POST':
        imp.delete()
        return redirect('importexport:ies:upload')
    context = {'imp': imp}
    return render(request, 'importexport/ies/cancel.html', context)
